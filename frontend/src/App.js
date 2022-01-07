import logo from './logo.svg';
import './App.scss';
import CodeDisplay from './CodeDisplay';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <CodeDisplay />
      </header>
    </div>
  );
}

export default App;
