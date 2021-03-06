import logo from './logo.svg';
import './App.scss';
import CodeDisplay from './CodeDisplay';
import GlitchText from './components/GlitchText';

function App() {
  return (
    <div className="App">
      <div id='header'>
        <GlitchText text='. . * * cats_can_code * * . .' classes='title pixelFont1' />
        <div className='subtitle pixelFont1 glow1'>
          <img id='catCodingImgLeft' src="/cat-dev.gif" />
          <img id='catCodingImgRight' src="/cat-dev.gif" />
          a project by team we_can_code
        </div>
      </div>
      <CodeDisplay />
      <div className='pixelFont1'>About cats_can_code:</div>
      <div id='projectIntro' className='pixelFont2 smallFont'>
        cats_can_code is a real time system that receives inputs from two cats (be it snoozing, chasing
        a laser pointer around or moving towards snacks) using motion sensors and a wifi module, and generates unique error-free code based on cat
        movements! Our team made this project with the sole goal of proving that since even cats can code (well sorta), anyone can!
      </div>
    </div>
  );
}

export default App;
