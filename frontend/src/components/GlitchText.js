import React, { useRef, useEffect, useState } from "react";
import ReactDOM from "react-dom";

function GlitchText(props) {
    var { text, classes } = props;

    useEffect(() => {

    }, []);

    return (
        <div className={'glitchText ' + classes}>
            {[1, 2, 3].map(i => {
                return <h1>{text}</h1>
            })}
        </div>
    );

}

export default GlitchText;