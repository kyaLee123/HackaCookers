import { useState } from "react";
import "./App.css";
import BiasSummarySheet from "./components/BiasSummarySheet";
import TargetBar from "./components/TargetBar";
import { Button, Heading } from "@chakra-ui/react";

function App() {
  const [categorySelected, setCategorySelected] = useState<Boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("");

  return (
    <>
      {" "}
      <div>
        <Heading size="4xl" color="teal" mt="10" mb="6" textAlign="center">
          TIKTOK BIAS BOT
        </Heading>
        <div className="flex justify-center mt-10">
          <TargetBar
            onSelectCategory={(selected, userText) => {
              setCategorySelected(selected);
              setSelectedCategory(userText);
            }}
          ></TargetBar>
        </div>

        {categorySelected && (
          <div>
            <BiasSummarySheet selectedCategory={selectedCategory} />
            <div className="flex justify-center mt-10">
              <Button
                colorPalette="teal"
                size="xl"
                mt="10"
                onClick={() => setCategorySelected(false)}
              >
                Reset
              </Button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default App;
