import {
  Box,
  Grid,
  GridItem,
  Heading,
  Slider,
  Text,
  Badge,
} from "@chakra-ui/react";

interface Props {
  selectedCategory: string;
}

const BiasSummarySheet = ({ selectedCategory }: Props) => {
  return (
    <Box maxW="6xl" mx="auto" mt="10" px="6">
      {/* Header */}
      <Heading size="2xl" mb="2" color="gray.100">
        Bias Summary
      </Heading>
      <Text mb="8" color="gray.400">
        Bias analysis overview for <b>{selectedCategory}</b>
      </Text>

      {/* Cards */}
      <Grid templateColumns="repeat(4, 1fr)" gap="6">
        {/* Relevancy Score */}
        <GridItem colSpan={2}>
          <Box
            p="6"
            bg="gray.900"
            borderRadius="xl"
            border="1px solid"
            borderColor="gray.700"
          >
            <Text color="gray.400" mb="2">
              Relevancy Score
            </Text>
            <Heading size="3xl" color="purple.400">
              4
            </Heading>
            <Text mt="2" color="gray.500">
              Measures alignment with the selected category.
            </Text>
          </Box>
        </GridItem>

        {/* Bot Status */}
        <GridItem colSpan={1}>
          <Box
            p="6"
            bg="red.800"
            borderRadius="xl"
            border="1px solid"
            borderColor="gray.700"
            h="100%"
          >
            <Text color="gray.400" mb="2">
              Bot Status
            </Text>
            <Badge colorScheme="green" mb="3">
              ACTIVE
            </Badge>
            <Text color="gray.200">
              Actively prioritizing content related to <b>{selectedCategory}</b>
              .
            </Text>
          </Box>
        </GridItem>

        {/* Metadata */}
        <GridItem colSpan={1}>
          <Box
            p="6"
            bg="blue.800"
            borderRadius="xl"
            border="1px solid"
            borderColor="gray.700"
            h="100%"
          >
            <Text color="gray.400" mb="3">
              Metadata
            </Text>
            <Text color="gray.200">Videos analyzed: 128</Text>
            <Text color="gray.200">Avg match: 62%</Text>
            <Text color="gray.200">Last update: 12s ago</Text>
          </Box>
        </GridItem>
      </Grid>

      {/* Slider Section */}
      <Box mt="10">
        <Text mb="2" color="gray.400">
          Bias Sensitivity
        </Text>
        <Slider.Root defaultValue={[40]} maxW="sm">
          <Slider.Control>
            <Slider.Track bg="gray.700">
              <Slider.Range bg="purple.400" />
            </Slider.Track>
            <Slider.Thumbs />
          </Slider.Control>
        </Slider.Root>
        <Text mt="2" fontSize="sm" color="gray.500">
          Adjust how aggressively the bot favors the selected category.
        </Text>
      </Box>
    </Box>
  );
};

export default BiasSummarySheet;
