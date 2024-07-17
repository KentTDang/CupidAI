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
          <button onClick={handleNewThread} className="new-chat-btn">
          <img src={assets.plus_icon} alt=""/> <p>New Chat</p>
          </button>
        : 
          <button onClick={handleNewThread} className="new-chat-btn">
          <img src={assets.plus_icon} alt="" />
          </button>
        }
      </div>
    </div>
  );
}
