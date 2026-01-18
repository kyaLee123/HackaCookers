import { useState } from "react";
import "./App.css";
import BiasSummarySheet from "./components/BiasSummarySheet";
import TargetBar from "./components/TargetBar";

function App() {
  const [categorySelected, setCategorySelected] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>("DANCE");
  return (
    <>
      {" "}
      <div>
        <TargetBar></TargetBar>

        {categorySelected && (
          <BiasSummarySheet selectedCategory={selectedCategory} />
        )}
      </div>
    </>
  );
}

export default App;
