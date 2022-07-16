import {
  Box,
  Text,
  HStack,
  Icon,
  IconButton,
  useBreakpointValue,
  useColorModeValue,
  Center,
  Img,
} from '@chakra-ui/react'
import { FaKeyboard } from 'react-icons/fa'
import { VscGithubInverted } from 'react-icons/vsc'
import { openInNewTab } from '../utils/OpenInNewTab'

export const Footer = () => {
  return (
    <Box bg="white" height='8vh' m='0' pt='3'>
      <Center>
        <Img src='/gonganbeian.png' />
        <Text fontSize="sm">粤公网安备 44010502002126号      粤ICP备2021133342号</Text>
      </Center>
    </Box>
  )
}