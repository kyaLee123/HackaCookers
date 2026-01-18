import { Box, Grid, GridItem, Heading, Slider, Text } from "@chakra-ui/react";

interface Props {
  selectedCategory: string;
}
const BiasSummarySheet = ({ selectedCategory }: Props) => {
  return (
    <div>
      <Heading size="2xl" mb="4">
        Bias Summary
      </Heading>
      <Heading size="md" mb="2">
        This is a summary of the bias analysis for {selectedCategory}.
      </Heading>
      <Grid templateColumns="repeat(4, 1fr)" gap="6">
        <GridItem colSpan={2} bg="pink">
          <Box h="20" _hover={{ bg: "green" }}>
            <Text textStyle="3xl" color="black">
              Relevancy Score:{" 4"}
            </Text>
          </Box>
        </GridItem>
        <GridItem colSpan={1} bg="blue">
          <Box h="20" _hover={{ bg: "green" }} />
          <Text>The bot is currently {""}</Text>
        </GridItem>
        <GridItem colSpan={1} bg="coral">
          <Box h="20" _hover={{ bg: "green" }} />
          <Text>METADATA</Text>
        </GridItem>
      </Grid>
      <Slider.Root width="200px" defaultValue={[40]}>
        <Slider.Control>
          <Slider.Track>
            <Slider.Range />
          </Slider.Track>
          <Slider.Thumbs />
        </Slider.Control>
      </Slider.Root>
    </div>
  );
};

export default BiasSummarySheet;
