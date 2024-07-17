import React, { useState } from "react";
import "../Sidebar/Sidebar.css";
import { assets } from "../../assets/assets";

export default function Sidebar() {

  const [extended, setExtended] = useState(false);

  const handleNewThread = () => {
    window.location.reload();
  }

  return (
    <div className="sidebar">
      <div className="top">
        <img onClick={()=> setExtended(!extended)} className="menu" src={assets.menu_icon} alt="" />
        {extended? 
        // <div className="new-chat">
          <button onClick={handleNewThread} className="new-chat-btn">
          <img src={assets.plus_icon} alt=""/> <p>New Chat</p>
          </button>
        // </div> 
        : 
        // <div className="new-chat">
          <button onClick={handleNewThread} className="new-chat-btn">
          <img src={assets.plus_icon} alt="" />
          </button>
        // </div> 
        }



        {extended? <div className="recent">
          <p className="recent-title">Recent</p>
          <div className="recent-entry">
            <img src={assets.message_icon} alt="" />
            <p>What is react...</p>
          </div>
        </div> : null}
      </div>
    </div>
  );
}
