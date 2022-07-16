import {
  Box,
  Switch,
  Text,
  HStack,
  VStack
} from '@chakra-ui/react'
import { ChangeEvent } from 'react'

interface switcherProps {
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
  isChecked: boolean
  title: string
  description: string
}

export const Switcher = (props:switcherProps) => {
  return (
    <Box py='5px'>
      <HStack spacing="10" justify="space-between" width='100%'>
        <VStack spacing="0" align="left">
          <Text fontSize='14px'>{props.title}</Text>
          <Text fontSize='8px' color="gray.600">{props.description}</Text>
        </VStack>
        <Switch isChecked={props.isChecked} onChange={props.onChange} />
      </HStack>
    </Box>
  )
}