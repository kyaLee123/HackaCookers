import {
  Combobox,
  HStack,
  Portal,
  Span,
  Spinner,
  useListCollection,
} from "@chakra-ui/react";
import { useState } from "react";
import { useAsync } from "react-use";

interface Category {
  name: string;
}

const TargetBar = () => {
  const [inputValue, setInputValue] = useState("");

  const { collection, set } = useListCollection<Category>({
    initialItems: [],
    itemToString: (item) => item.name,
    itemToValue: (item) => item.name,
  });

  const state = useAsync(async () => {
    const response = await fetch(
      `http://localhost:8000/categories?q=${encodeURIComponent(inputValue)}`,
    );
    const data = await response.json();
    set((data.items ?? []).map((name: string) => ({ name })));
  }, [inputValue, set]);
  return (
    <div>
      <Combobox.Root
        width="320px"
        collection={collection}
        placeholder="Example: Music, Art, Sports"
        onInputValueChange={(e) => setInputValue(e.inputValue)}
        positioning={{ sameWidth: false, placement: "bottom-start" }}
      >
        <Combobox.Label>Pick a target category to optmize bias</Combobox.Label>

        <Combobox.Control>
          <Combobox.Input placeholder="What is your target category??" />
          <Combobox.IndicatorGroup>
            <Combobox.ClearTrigger />
            <Combobox.Trigger />
          </Combobox.IndicatorGroup>
        </Combobox.Control>
        <Portal>
          <Combobox.Positioner>
            <Combobox.Content minW="sm">
              {state.loading ? (
                <HStack p="2">
                  <Spinner size="xs" borderWidth="1px" />
                  <Span>Loading...</Span>
                </HStack>
              ) : state.error ? (
                <Span p="2" color="fg.error">
                  Error fetching
                </Span>
              ) : (
                collection.items?.map((category) => (
                  <Combobox.Item key={category.name} item={category}>
                    <HStack justify="space-between" textStyle="sm">
                      <Span fontWeight="medium" truncate>
                        {category.name}
                      </Span>
                    </HStack>
                    <Combobox.ItemIndicator />
                  </Combobox.Item>
                ))
              )}
            </Combobox.Content>
          </Combobox.Positioner>
        </Portal>
      </Combobox.Root>
    </div>
  );
};

export default TargetBar;
