import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faBell, faBellSlash, faExclamationCircle, faSave } from '@fortawesome/free-solid-svg-icons'
import calvin from './calvin.jpg';
import './App.css';

const GET_URL = "https://s3.eu-central-1.amazonaws.com/xxx"
const SET_URL = "https://xxx.execute-api.eu-central-1.amazonaws.com/xxx"

const STATUS = {
  DEFAULT: 0,
  SAVING: 1,
  ERROR: 2
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      time: 0,
      active: false,
      alarmTimeString: '00:00',
      status: STATUS.DEFAULT
    };

    this.handleTimeChange = this.handleTimeChange.bind(this);
    this.handleActiveChange = this.handleActiveChange.bind(this);
    this.submit = this.submit.bind(this);
  }
  componentDidMount() {
    fetch(GET_URL)
      .then(response => response.json())
      .then(data => {
        var alarmTimeString = (new Date(data.time * 1000)).toLocaleTimeString(undefined, {hour12: false})
        this.setState({
          time: data.time,
          active: data.active,
          alarmTimeString: alarmTimeString,
          status: STATUS.DEFAULT
        })
      })
      .catch((error) => {
        this.setState({status: STATUS.ERROR})
      });

  }
  handleTimeChange(event) {
    this.setState({ alarmTimeString: event.target.value});

    var seconds = event.target.valueAsNumber / 1000
    if (!isNaN(seconds)) {
      var alarmDate = new Date()
      alarmDate.setHours(0, 0, 0, 0)
      alarmDate.setSeconds(event.target.valueAsNumber / 1000)
      if (alarmDate.getTime() < Date.now()) {
        alarmDate.setDate(alarmDate.getDate() + 1);
      }
      this.setState({ time: alarmDate.getTime() / 1000, active: true, status: STATUS.SAVING }, this.submit);
    }
  }
  handleActiveChange(event) {
    event.preventDefault();
    this.setState({ active: !this.state.active, status: STATUS.SAVING }, this.submit);
  }
  submit() {
    fetch(SET_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        time: this.state.time,
        active: this.state.active
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Response:', data);
        let status = (data.success) ? STATUS.DEFAULT : STATUS.ERROR
        this.setState({status: status})
      })
      .catch((error) => {
        this.setState({status: STATUS.ERROR})
      });
  }
  render() {
    let alarmIcon;
    if (this.state.active) {
      alarmIcon = <FontAwesomeIcon icon={faBell} size="2x" />
    } else {
      alarmIcon = <FontAwesomeIcon icon={faBellSlash} size="2x" />
    }

    let statusIcon;
    if (this.state.status === STATUS.ERROR) {
      statusIcon = <FontAwesomeIcon icon={faExclamationCircle} className="status_icon" size="2x" />
    } else if (this.state.status === STATUS.SAVING) {
      statusIcon = <FontAwesomeIcon icon={faSave} className="status_icon" size="2x" />
    }

    return (
      <div className="App">
        {statusIcon}
        <form>
          <input
            className="time"
            type="time"
            value={this.state.alarmTimeString}
            onChange={this.handleTimeChange}
          />
          <button className="active" onClick={this.handleActiveChange}>
            {alarmIcon}
          </button>
        </form>
        <img src={calvin} className="calvin" alt="calvin" />
      </div>
    );
  }
}

export default App;
