import React, {useState, useEffect} from 'react'
import axios from 'axios';
import './Main.css'
import { assets } from '../../assets/assets'

export default function Main() {

    const [task, setTask] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAPI();
  }, [])

  const fetchAPI = async () => {
    try {
      const response = await axios.get('http://localhost:8080/api/disaster-response');
      setTask(response.data);
    }catch (e) {
      console.error(e);
    }
  };

  const handleInputChange = (e) => {
    setTask(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResults([]);
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8080/api/disaster-response', { task });
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setTask('');
    }
  };

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
            <div className="results">
        {results.map((item, index) => (
          <>
          <div key={index}>
            <pre>{JSON.stringify(item, null, 2)}</pre>
          </div>
          </>
          
        ))}
      </div>
            <div className="main-bottom">
                {/* <div className="search-box"> */}
                    <form onSubmit={handleSubmit} className='search-box'>
                        <input 
                        type="text"
                        value={task}
                        onChange={handleInputChange}
                        placeholder='Enter a prompt here'/>
                        <div>
                        <button type='submit'><img src={assets.send_icon} alt="" /></button>
                        </div>
                    </form>
                    
                {/* </div> */}
                <p className='bottom-info'>This AI can make mistakes. Check important info.</p>
            </div>
        </div>
    </div>
  )
}
