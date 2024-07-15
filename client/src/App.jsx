import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from "axios"

function App() {
  const [array, setArray] = useState([]);

  const fetchAPI = async () => {
    try {
      const response = await axios.get("http://localhost:8080/api/disaster-response");
      console.log(response);
      setArray(response.data);
    } catch(e) {
      console.error("Could not fetch api: ", e);
    }
  }

  useEffect(() => {
    fetchAPI();
  }, [])

  return (
    <>
      <div className="read-the-docs">
        {array.map((plan, index) => (
          <div key={index}>
            <pre>{JSON.stringify(plan, null, 2)}</pre>
          </div>
        ))}
      </div>
    </>
  )
}

export default App
