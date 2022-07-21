import {
    Textarea,
    Box,
    Text,
    Icon,
    VStack,
    HStack,
    Divider,
} from "@chakra-ui/react";
import * as React from "react"
import textarea_caret from "textarea-caret";
import { AiFillCaretLeft, AiFillCaretRight } from "react-icons/ai";

interface Answer {
    answer: string;
    partition: Array<string>;
    probability: number;
    "process_to": number;
}

interface ServerResponse {
    status: number;
    data: Array<Answer>;
    totalSize: number;
    computeTime: number;
}

interface State {
    currInput: string,
    currCandidates: Array<Answer>,
    currCandidateStart: number,
    displayText: string,
    candidateText: string,
    active: boolean,
    lastKeydown: string,
    IMEcontainerLeft: string,
    IMEcontainerTop: string,
    displayContainer: boolean,
    hasNextPage: boolean,
    hasPrevPage: boolean,
}

interface TimeStatistic {
    start: number;
    total: number;
    hmm: number;
    fetch: number;
    wait: number;
    moveContainer: number;
    render: number;
    javascript: number;
}

// a function to send a toasted message to the user
interface sendToast{
    (
        title: string,
        status: "success" | "error" | "warning" | "info",
        isClosable: boolean,
        description: string,
    ): void;
}

const digitsReg = new RegExp('^[1-9]+$');
const pageSize = 10;
const extraBorder = 8;
const serverURL = "/api/candidate";
// timeout in milliseconds
const TIMEOUT = 10000;

const defaultState: State = {
    currInput: '',
    currCandidates: [],
    currCandidateStart: 0,
    displayText: '',
    candidateText: '',
    active: false,
    lastKeydown: '',
    IMEcontainerLeft: '',
    IMEcontainerTop: '',
    displayContainer: false,
    hasNextPage: false,
    hasPrevPage: false,
};

function isLetter(c: string): boolean {
    return c.length === 1 && c.toLowerCase() !== c.toUpperCase();
}

export class InputArea extends React.Component<{ fix: boolean, partical: boolean,toast:sendToast }, {}> {
    private queue: Promise<void>;
    private InputAreaRef: React.RefObject<HTMLTextAreaElement>;
    private _state: State;
    private timeStatistic: TimeStatistic;
    private prevState: State;
    private queueLen: number;
    private popLen: number;

    constructor(props: { fix: boolean, partical: boolean,toast:sendToast }) {
        super(props);
        this.queue = Promise.resolve();
        this.queueLen = 0;
        this.popLen = 0;
        this.InputAreaRef = React.createRef();
        this._state = defaultState;
        this.prevState = defaultState;
        this.timeStatistic = {
            start: 0,
            total: 0,
            hmm: 0,
            fetch: 0,
            wait: 0,
            moveContainer: 0,
            render: 0,
            javascript: 0,
        };
    }

    private initTimeStatistic(start: number) {
        this.timeStatistic.start = start;
        this.timeStatistic.total = 0;
        this.timeStatistic.hmm = 0;
        this.timeStatistic.fetch = 0;
        this.timeStatistic.wait = new Date().getTime() - start;
        this.timeStatistic.moveContainer = 0;
        this.timeStatistic.render = 0;
        this.timeStatistic.javascript = 0;
    }

    private moveCandidateContainer() {
        // Move the container to the correct position
        this.timeStatistic.moveContainer = new Date().getTime();

        if (this.InputAreaRef.current === null) {
            console.error("input area is undefined");
            return;
        }
        const currCursor = textarea_caret(this.InputAreaRef.current, this.InputAreaRef.current.selectionStart);
        console.debug("currCursor: ", currCursor);

        const inputAreaLeft = this.InputAreaRef.current.getBoundingClientRect().left;
        const inputAreaTop = this.InputAreaRef.current.getBoundingClientRect().top;
        const textFontSize = parseFloat(getComputedStyle(this.InputAreaRef.current, null).getPropertyValue('font-size'));
        const imeLeft = inputAreaLeft + currCursor.left;
        const imeTop = inputAreaTop + currCursor.top + textFontSize + extraBorder;

        this._state.IMEcontainerLeft = `${imeLeft}px`;
        this._state.IMEcontainerTop = `${imeTop}px`;

        this.timeStatistic.moveContainer = new Date().getTime() - this.timeStatistic.moveContainer;
    }

    private setCandidates(candidates: Array<Answer>) {
        // set candidates to state
        let newCandidateText = "";
        candidates.forEach((answer: Answer, index: number) => {
            newCandidateText += `${index + 1}. ${answer.answer} `;
        });
        this._state.displayContainer = true;
        this._state.currCandidates = candidates;
        this._state.candidateText = newCandidateText;

        // set display text
        this._state.displayText = "";
        let counter = 0;
        candidates[0].partition.forEach((partition: string) => {
            this._state.displayText += partition;
            counter += partition.length;
            if (this._state.currInput.charAt(counter) === `'`) {
                this._state.displayText += `'`;
                counter++;
            } else {
                this._state.displayText += ` `;
            }
        });
        if (counter < this._state.currInput.length) {
            this._state.displayText += this._state.currInput.slice(counter);
        }
        this.moveCandidateContainer();
    }

    private async getCandidates() {
        // Fetch candidates from server
        const url = `${serverURL}?start=${this._state.currCandidateStart}&size=${pageSize}&text=${this._state.currInput}&fix=${this.props.fix}&partical=${this.props.partical}`;
        try{
            this.timeStatistic.fetch = new Date().getTime();
            // ser timeout
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), TIMEOUT)
            const response = await fetch(url, { signal: controller.signal });
            this.timeStatistic.fetch = new Date().getTime() - this.timeStatistic.fetch;
            if (response.status === 200) {
                const json: ServerResponse = await response.json();
                this._state.hasNextPage = (json.totalSize > this._state.currCandidateStart + pageSize);
                this._state.hasPrevPage = (this._state.currCandidateStart >= pageSize);
                this.setCandidates(json.data);
                this.timeStatistic.hmm = json.computeTime;
            } else {
                console.error("get candidates failed: ", await response.text());
                throw new Error(`Status code ${response.status}`);
            }
        }catch(e){
            this._state=structuredClone(this.prevState);
            let errMsg:string="Unknown error, please check console";
            if(e instanceof Error){
                errMsg=(e.name==="AbortError")?`Request time out!`:`${e.name}: ${e.message}`;
            }
            this.props.toast(
                "网络请求出错，请稍后再试",
                "error",
                true,
                errMsg,
            )
            console.error("get candidates failed: ", e);
            // cancel all requests after error
            this.popLen = this.queueLen;
        }
    }

    private async getMoreCandidates() {
        // increase currCandidateStart and fetch candidates by getCandidates
        if (this._state.hasNextPage) {
            this._state.currCandidateStart += pageSize;
            await this.getCandidates();
        }
    }

    private async getLessCandidates() {
        // decrease currCandidateStart and fetch candidates by getCandidates
        if (this._state.hasPrevPage) {
            this._state.currCandidateStart -= pageSize;
            await this.getCandidates();
        }
    }

    private async startComposition() {
        this._state.currCandidateStart = 0;
        this._state.displayContainer = true;
        this._state.active = true;
        await this.getCandidates();
    }

    private async endComposition(n: number = 0) {
        if (this.InputAreaRef.current === null) {
            console.error("input area is undefined");
            throw new Error("input area is undefined");
        }
        if (n === 0) {
            this.InputAreaRef.current.value += this._state.currInput;
            //Refresh state
        } else {
            const seletedCandidate = this._state.currCandidates[n - 1];
            this.InputAreaRef.current.value += seletedCandidate.answer;
            let inputLeft = this._state.currInput;
            for (let i = 0; i < seletedCandidate["process_to"];) {
                if (inputLeft.charAt(0) === `'`) {
                    inputLeft = inputLeft.slice(1);
                } else {
                    inputLeft = inputLeft.slice(1);
                    i++;
                }
            }
            while (inputLeft.charAt(0) === `'`) inputLeft = inputLeft.slice(1);
            if (inputLeft.length !== 0){
                this._state.currInput= inputLeft;
                await this.startComposition();
                return;
            }
        }
        this._state.currInput = '';
        this._state.currCandidates = [];
        this._state.currCandidateStart = 0;
        this._state.displayText = '';
        this._state.candidateText = "";
        this._state.active = false;
        this._state.displayContainer = false;
        this._state.hasNextPage = false;
        this._state.hasPrevPage = false;
    }

    private async handleKeydown(evt: React.KeyboardEvent<HTMLTextAreaElement>, start: number) {
        this.queueLen--;
        if (this.popLen > 0) {
            this.popLen--;
            return;
        }
        this.prevState = structuredClone(this._state);
        this.initTimeStatistic(start);
        if (evt.key === 'Shift' && (evt.altKey || evt.ctrlKey)) {
            return;
        }
        this._state.lastKeydown = evt.key;
        if (this._state.active) {
            if (evt.key === 'Enter') {
                await this.endComposition(0);
            } else if (evt.code === 'Space') {
                await this.endComposition(1);
            } else if (evt.key.match(digitsReg)) {
                await this.endComposition(parseInt(evt.key));
            } else if (evt.code === 'Equal') {
                await this.getMoreCandidates();
            } else if (evt.code === 'Minus') {
                await this.getLessCandidates();
            } else if (evt.code === 'Backspace') {
                this._state.currInput = this._state.currInput.slice(0, -1);
                if (this._state.currInput.length === 0) {
                    this._state.currCandidates = [];
                    this._state.candidateText = "";
                    this._state.active = false;
                    this._state.displayContainer = false;
                    this._state.hasNextPage = false;
                    this._state.hasPrevPage = false;
                } else {
                    await this.startComposition();
                }
            }
            console.debug("State Update: ", this._state);
            this.timeStatistic.render = new Date().getTime();
            this.forceUpdate();
            this.timeStatistic.render = new Date().getTime() - this.timeStatistic.render;
        }
        if (!evt.key.match(digitsReg) && (isLetter(evt.key) || (evt.key === `'` && this._state.active))) {
            this._state.currInput += evt.key;
            await this.startComposition();
            console.debug("State Update: ", this._state);
            this.timeStatistic.render = new Date().getTime();
            this.forceUpdate();
            this.timeStatistic.render = new Date().getTime() - this.timeStatistic.render;
        }
        this.timeStatistic.total = new Date().getTime() - this.timeStatistic.start;
        this.timeStatistic.javascript = this.timeStatistic.total - this.timeStatistic.fetch - this.timeStatistic.moveContainer - this.timeStatistic.render - this.timeStatistic.wait;
        console.debug("Time statistic: ", structuredClone(this.timeStatistic));
    }


    private keyDown(evt: React.KeyboardEvent<HTMLTextAreaElement>) {
        let start = new Date().getTime();
        console.debug("keyDown: ", evt);
        if (this._state.active || (!evt.key.match(digitsReg) && isLetter(evt.key))) {
            evt.preventDefault();
            evt.stopPropagation();
        }
        this.queue = this.queue.then(async () => { await this.handleKeydown(evt, start); });
        this.queueLen++;
    }

    render(): React.ReactNode {
        return (
            <Box height="100%" >
                <Textarea
                    placeholder="请在此输入"
                    height="100%"
                    resize='none'
                    bg='white'
                    id="input-area"
                    onKeyDown={(evt) => { this.keyDown(evt); }}
                    ref={this.InputAreaRef}
                />
                <Box
                    display={this._state.displayContainer ? 'block' : 'none'}
                    position="absolute"
                    left={this._state.IMEcontainerLeft}
                    top={this._state.IMEcontainerTop}
                    zIndex={this._state.displayContainer ? 100 : -1}
                    bg='white'
                    fontSize="16px"
                    border="1px solid #ccc"
                    borderRadius="4px"
                    padding="3px 10px"
                    boxShadow='0px 1px 4px rgba(0, 0, 0, 0.25)'
                >
                    <VStack>
                        <HStack justify="space-between" width='100%'>
                            <Text fontWeight={600}>{this._state.displayText}</Text>
                            <HStack>
                                <Icon as={AiFillCaretLeft} color={this._state.hasPrevPage ? '#000' : '#ccc'} />
                                <Icon as={AiFillCaretRight} color={this._state.hasNextPage ? '#000' : '#ccc'} />
                            </HStack>
                        </HStack>
                        <Divider m='1px !important' p='0' borderColor='gray.400' />
                        <Text m='0 !important' fontWeight={400}>{this._state.candidateText}</Text>
                    </VStack>
                    {/* <Grid
                        templateAreas={`"input prev next"
                        "candidate candidate candidate""`}
                        gridTemplateRows={'50% 50%'}
                        gridTemplateColumns={'90% 5% 5%'}
                    >
                        <GridItem area="input">
                            <Text>{this.state.displayText}</Text>
                        </GridItem>
                        <GridItem area="prev">
                            <Icon as={AiFillCaretLeft} color={this.state.hasPrevPage ? '#000' : '#ccc'} />
                        </GridItem>
                        <GridItem area="next">
                            <Icon as={AiFillCaretRight} color={this.state.hasNextPage ? '#000' : '#ccc'} />
                        </GridItem>
                        <GridItem area="candidate">
                            <Text>{this.state.candidateText}</Text>
                        </GridItem>
                    </Grid> */}
                </Box>
            </Box>
        );
    }
}