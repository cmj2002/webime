import * as React from "react"
import {
  ChakraProvider,
  Box,
  Grid,
  GridItem,
  theme,
  Switch,
  Divider,
} from "@chakra-ui/react"
import { Navbar } from "./components/navbar"
import { Footer } from "./components/footer"
import ReactMarkdown from 'react-markdown'
import './style/markdown.css'
import { Helmet } from 'react-helmet';
import { InputArea } from "./components/InputArea"
import { Switcher } from "./components/Switcher"

export const App = () => {
  const [fix,setFix] = React.useState(true);
  const [partical,setPartical] = React.useState(true);
  return (
    <ChakraProvider theme={theme}>
      <Grid
        templateAreas={`"header header"
                  "readme right"
                  "textarea right"
                  "footer footer"`}
        gridTemplateRows={'12% 28% auto 8%'}
        gridTemplateColumns={'75% 25%'}
        bg="gray.100"
        h='100vh'
        w='100vw'
      >
        <GridItem area={'header'}>
          <Navbar />
        </GridItem>
        <GridItem area={'readme'}>
          <Box p='3' m='3' bg="white" borderWidth='3px' borderRadius='lg' borderColor="rgba(255, 255, 255, .5)" overflow='hidden'>
            <ReactMarkdown className="markdown-body">
              {"## 简介\n\n"
                + "这是一个简单的在线中文输入法，后端基于 HMM 模型，前端基于 `React` 和 `Chakra UI`\n\n"
                + "建议仅在电脑端上使用，**使用时请关闭电脑自带的输入法**。"
              }
            </ReactMarkdown>
          </Box>
        </GridItem>
        <GridItem m='3' area={'textarea'}>
          <InputArea fix={fix} partical={partical}/>
        </GridItem>
        <GridItem area={'right'}>
          <Box p='3' mr='3' my='3' bg="white" borderWidth='3px' borderRadius='lg' borderColor="rgba(255, 255, 255, .5)" overflow='hidden' height='calc(100% - 1.5rem)'>
            <ReactMarkdown className="markdown-body">{"## 选项\n\n"}</ReactMarkdown>
            <Switcher 
              isChecked={fix} 
              onChange={() => {setFix(!fix)}}
              title="自动纠错"
              description="尝试纠正输入中的错误"
            />
            <Switcher
              isChecked={partical}
              onChange={() => {setPartical(!partical)}}
              title="允许部分切分"
              description="候选词可能只对应输入的前几个字"
            />
            <ReactMarkdown className="markdown-body">
              {"## 如何使用\n\n"
                + "* 通过键盘上的字母键输入拼音\n"
                + "* 通过数字键选择候选词\n"
                + "  * 空格键选择第一个候选词\n"
                + "* 如果对分词不满意，可以用分号键人工分词\n"
                + "* `+`、`-` 键可以进行翻页\n"
                + "* 不支持 Shift 切换语言（以免与自带输入法冲突）\n"
              }
            </ReactMarkdown>
          </Box>
        </GridItem>
        <GridItem area={'footer'}>
          <Footer />
        </GridItem>
      </Grid>
    </ChakraProvider>
  )
}
