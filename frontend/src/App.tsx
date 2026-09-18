import { useState } from "react";
import SwipeScreen from "./SwipeScreen";
import WikiScreen from "./WikiScreen";
import "./App.css";

type Screen = "swipe" | "wiki";

function App() {
  const [screen, setScreen] = useState<Screen>("swipe");

  return (
    <div className="app">
      <header className="header">
        <h1>Swipe Wiki</h1>
        <p className="tagline">タイトルとタグで技術記事を一次選別</p>
      </header>

      <nav className="tabs">
        <button
          type="button"
          className={screen === "swipe" ? "active" : ""}
          onClick={() => setScreen("swipe")}
        >
          スワイプ
        </button>
        <button
          type="button"
          className={screen === "wiki" ? "active" : ""}
          onClick={() => setScreen("wiki")}
        >
          保存一覧
        </button>
      </nav>

      {screen === "swipe" ? <SwipeScreen /> : <WikiScreen />}
    </div>
  );
}

export default App;
