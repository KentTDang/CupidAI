import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Main.css";
import { assets } from "../../assets/assets";
import { TailSpin } from "react-loader-spinner";

export default function Main() {
  const [task, setTask] = useState("");
  const [results, setResults] = useState([]);
  const [showResult, setShowResult] = useState(false);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const [planner, setPlanner] = useState("");
  const [research, setResearch] = useState([]);
  const [draftText, setDraftText] = useState("");

  const handleInputChange = (e) => {
    setTask(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResults([]);
    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:8080/api/disaster-response",
        { task }
      );

      const generateData = response.data.find(
        (item) => item.generate
      )?.generate;

      const generatePlan = response.data.find(
        (item) =>item.planner
      )?.planner;

      const generateResearch = response.data.find((item)=> item.research_plan)?.research_plan;

      setShowResult(true);

      setDraftText(generateData.draft);
      setPlanner(generatePlan.plan);
      setResearch(generateResearch.content);
    
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main">
      <div className="nav">
        <p>Cupid AI</p>
        <img src="" alt="" />
      </div>
      <div className="main-container">
        {!showResult ? (
          <div>
            <div className="greet">
              <p>
                <span>Welcome</span>
                <img src={assets.cat_gif} alt="" />
              </p>
              <p>How can I help you today?</p>
            </div>
            <div className="cards">
              <div className="card">
                <p>Suggest beautiful places to see on an upcoming road trip</p>
              </div>
              <div className="card">
                <p>Suggest beautiful places to see on an upcoming road trip</p>
              </div>
              <div className="card">
                <p>Suggest beautiful places to see on an upcoming road trip</p>
              </div>
              <div className="card">
                <p>Suggest beautiful places to see on an upcoming road trip</p>
              </div>
            </div>
          </div>
        ) : null}
        {planner && (
          <div>
            <h3>Plan</h3>
            <p>{planner}</p>
          </div>
        )}
        {research && (
          <div>
            <h3>Research</h3>
            <p>{research}</p>
          </div>
        )}
        {draftText && (
          <div>
            <h3>Conclusion</h3>
            <p>{draftText}</p>
          </div>
        )}
        <div className="main-bottom">
          {!loading ? (
            <form onSubmit={handleSubmit} className="search-box">
              <input
                type="text"
                value={task}
                onChange={handleInputChange}
                placeholder="Enter a prompt here"
              />
              <div>
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={!task.trim()}
                >
                  <img src={assets.send_icon} alt="" />
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleSubmit} className="search-box">
              <input
                type="text"
                value={task}
                onChange={handleInputChange}
                placeholder="Enter a prompt here"
                disabled
              />
              <div>
                <TailSpin height="25" color="#585858" width="24" />
              </div>
            </form>
          )}

          <p className="bottom-info">
            Cupid AI can make mistakes. Check important info.
          </p>
        </div>
      </div>
    </div>
  );
}
