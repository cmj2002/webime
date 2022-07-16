import {
  Box,
  Text,
  HStack,
  Icon,
  IconButton,
  useBreakpointValue,
  useColorModeValue,
} from '@chakra-ui/react'
import { FaKeyboard } from 'react-icons/fa'
import { VscGithubInverted } from 'react-icons/vsc'
import { openInNewTab } from '../utils/OpenInNewTab'

export const Navbar = () => {
  // const isDesktop = useBreakpointValue({ base: false, lg: true })
  return (
    <Box as="nav" bg="white" pb='3' pt='3' boxShadow={useColorModeValue('lg', 'lg-dark')} width='100%'>
      <HStack spacing="10" justify="space-between" width='100%' px='10'>
        <HStack spacing="5">
          <Icon as={FaKeyboard} size='2xl'/>
          <Text fontSize='lg'>在线拼音输入法</Text>
        </HStack>
        <HStack spacing="3">
            {/* <ColorModeSwitcher /> */}
            <IconButton
              icon={<VscGithubInverted />}
              aria-label='GitHub Repo'
              size="md"
              fontSize="lg"
              variant="ghost"
              color="current"
              onClick={() => openInNewTab('https://github.com/cmj2002/')} />
          </HStack>
      </HStack>
    </Box>
  )
}