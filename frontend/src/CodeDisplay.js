import React, { Component } from 'react';

class CodeDisplay extends Component {
    state = {
        data: null,
    }

    fetchData = async () => {
        const url = 'https://code-gen-martini.herokuapp.com/code';
        const response = await fetch(url);
        response.text()
            .then(data => {
                if (response.status == 200) {
                    console.log(data);
                    this.setState({data: data})   
                } else {
                    console.log(response.status);
                }}
            );
    } 

    async componentDidMount(){
        await this.fetchData(); //waits for data 
   
        this.intervalId = setInterval(() => {
           this.fetchData();
        }, 1000); //polls for data every 1s
    }

    componentWillUnmount() {
        clearInterval(this.intervalId);
    } 

    render() {
        const {data} = this.state;
        return (
            <div>
                <h3>{data}</h3>
            </div>
        )
    }

}

export default CodeDisplay;