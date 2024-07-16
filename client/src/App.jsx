import { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [task, setTask] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [testData, setTestData] = useState([]);

  useEffect(() => {
    fetchAPI();
  }, [])

  const fetchAPI = async () => {
    try {
      const response = await axios.get('http://localhost:8080/api/disaster-response');
      setTestData(response.data);
      console.log(testData);
    }catch (e) {
      console.error(e);
    }
  };

  const handleInputChange = (e) => {
    setTask(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8080/api/disaster-response', { task });
      setResults(response.data);
      console.log(response);
      console.log(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={task}
          onChange={handleInputChange}
          placeholder="Enter task"
        />
        <button type="submit">Submit</button>
      </form>
      <div className="results">
        {results.map((item, index) => (
          <div key={index}>
            <pre>{JSON.stringify(item, null, 2)}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
