import React from 'react'
import './Main.css'
import { assets } from '../../assets/assets'

export default function Main() {
  return (
    <div className="main">
        <div className="nav">
            <p>Tavily</p>
            <img src="" alt="" />
        </div>
        <div className="main-container">
            <div className="greet">
                <p><span>Hello, Person</span></p>
                <p>How can I help you today?</p>
            </div>
            <div className="cards">
                <div className="card">
                    <p>Suggest beautiful places to see on an upcoming road trip</p>
                    <img src={assets.compass_icon} alt="" />
                </div>
                <div className="card">
                    <p>Suggest beautiful places to see on an upcoming road trip</p>
                    <img src={assets.bulb_icon} alt="" />
                </div>
                <div className="card">
                    <p>Suggest beautiful places to see on an upcoming road trip</p>
                    <img src={assets.message_icon} alt="" />
                </div>
                <div className="card">
                    <p>Suggest beautiful places to see on an upcoming road trip</p>
                    <img src={assets.code_icon} alt="" />
                </div>
            </div>
            <div className="main-bottom">
                <div className="search-box">
                    <input type="text" placeholder='Enter a prompt here'/>
                    <div>
                        <img src={assets.send_icon} alt="" />
                    </div>
                </div>
                <p className='bottom-info'>This AI can make mistakes. Check important info.</p>
            </div>
        </div>
    </div>
  )
}
