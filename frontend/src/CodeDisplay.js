import React, { Component } from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter'
import {
    a11yDark, a11yLight, agate, anOldHope, androidstudio, arduinoLight, arta, ascetic, atelierCaveDark,
    atelierCaveLight, atelierDuneDark, atelierDuneLight, atelierEstuaryDark, atelierEstuaryLight, atelierForestDark, atelierForestLight,
    atelierHeathDark, atelierHeathLight, atelierLakesideDark, atelierLakesideLight, atelierPlateauDark, atelierPlateauLight, atelierSavannaDark,
    atelierSavannaLight, atelierSeasideDark, atelierSeasideLight, atelierSulphurpoolDark, atelierSulphurpoolLight, atomOneDark,
    atomOneDarkReasonable, atomOneLight, brownPaper, codepenEmbed, colorBrewer, darcula, dark, defaultStyle, docco, dracula, far, foundation,
    github, githubGist, gml, googlecode, gradientDark, gradientLight, grayscale, gruvboxDark, gruvboxLight, hopscotch, hybrid, idea, irBlack,
    isblEditorDark, isblEditorLight, kimbieDark, kimbieLight, lightfair, lioshi, magula, monoBlue, monokai, monokaiSublime, nightOwl, nnfx,
    nnfxDark, nord, obsidian, ocean, paraisoDark, paraisoLight, pojoaque, purebasic, qtcreatorDark, qtcreatorLight, railscasts, rainbow, routeros,
    schoolBook, shadesOfPurple, solarizedDark, solarizedLight, srcery, stackoverflowDark, stackoverflowLight, sunburst, tomorrow, tomorrowNight,
    tomorrowNightBlue, tomorrowNightBright, tomorrowNightEighties, vs, vs2015, xcode, xt256, zenburn
} from 'react-syntax-highlighter/dist/esm/styles/hljs';

class CodeDisplay extends Component {
    state = {
        data: '',
    }

    fetchData = async () => {
        const url = 'https://code-gen-martini.herokuapp.com/code';
        const response = await fetch(url);
        response.text()
            .then(data => {
                if (response.status == 200) {
                    console.log(data);
                    this.setState({ data: data })
                } else {
                    console.log(response.status);
                }
            }
            );
    }

    async componentDidMount() {
        await this.fetchData(); //waits for data 

        this.intervalId = setInterval(() => {
            this.fetchData();
        }, 1000); //polls for data every 1s
    }

    componentWillUnmount() {
        clearInterval(this.intervalId);
    }

    render() {
        const { data } = this.state;
        return (
            <div>
                <SyntaxHighlighter language='python' customStyle={{
                    width: 'calc(100% - 100px)',
                    position: 'relative',
                    margin: 'auto',
                    background: 'none',
                    border: '2px solid white',
                    filter: 'hue-rotate(90deg)',
                    // boxShadow: '0px 0px 21px 0px #a49fede6'
                }} style={vs2015}>
                    {data}
                </SyntaxHighlighter>
                <h3></h3>
            </div>
        )
    }

}

export default CodeDisplay;