import { useEffect, useState } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar/Sidebar';
import Main from './components/Main/Main';

function App() {
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

    <>
      <Sidebar />
      <Main />
    </>
    // <div className="App">
    //   <form onSubmit={handleSubmit}>
    //     <input
    //       type="text"
    //       value={task}
    //       onChange={handleInputChange}
    //       placeholder="Enter task"
    //     />
    //     <button type="submit">Submit</button>
    //   </form>
    //   <div className="results">
    //     {results.map((item, index) => (
    //       <>
    //       <div key={index}>
    //         <pre>{JSON.stringify(item, null, 2)}</pre>
    //       </div>
    //       </>
          
    //     ))}
    //   </div>
    // </div>
  );
}

export default App;
