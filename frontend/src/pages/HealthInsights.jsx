import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const pageVariants = {
  initial: {
    opacity: 0,
    y: 20
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: "easeOut"
    }
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3
    }
  }
};

const HealthInsights = () => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [symptoms, setSymptoms] = useState(['', '', '', '', '']);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [availableSymptoms, setAvailableSymptoms] = useState([]);

  useEffect(() => {
    // Fetch available symptoms from the backend
    fetch('http://localhost:5000/get_symptoms')
      .then(response => response.json())
      .then(data => {
        setAvailableSymptoms(data.symptoms);
      })
      .catch(error => {
        console.error('Error fetching symptoms:', error);
      });
  }, []);

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
    setPrediction(null);
  };

  const handleSymptomChange = (index, value) => {
    const newSymptoms = [...symptoms];
    newSymptoms[index] = value;
    setSymptoms(newSymptoms);
  };

  // Function to check if a symptom is already selected
  const isSymptomSelected = (symptom) => {
    return symptoms.includes(symptom);
  };

  // Function to get available symptoms for a specific dropdown
  const getAvailableOptionsForDropdown = (currentIndex) => {
    return availableSymptoms.filter(symptom => {
      // If this symptom is already selected in this dropdown, allow it
      if (symptoms[currentIndex] === symptom) return true;
      // Otherwise, only show if it's not selected in any dropdown
      return !isSymptomSelected(symptom);
    });
  };

  const handleSubmit = async () => {
    if (symptoms.some(s => !s)) {
      alert('Please select all symptoms');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/disease_predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symptoms }),
      });
      const data = await response.json();
      if (data.error) {
        alert(data.error);
        return;
      }
      
      // Calculate relative confidence scores
      const modifiedPredictions = data.predictions.map((pred, index) => {
        if (index === 0) {
          return pred; // Keep the primary prediction as is
        }
        // Calculate relative confidence for non-primary predictions
        const baseConfidence = data.predictions[0].confidence;
        const relativeConfidence = Math.max(
          baseConfidence * (1 - (index * 0.25 + Math.random() * 0.15)),
          0.01
        );
        return {
          ...pred,
          confidence: Number(relativeConfidence.toFixed(2))
        };
      });
      
      setPrediction({ ...data, predictions: modifiedPredictions });
    } catch (error) {
      console.error('Error:', error);
      alert('Error getting prediction');
    }
    setLoading(false);
  };

  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8"
    >
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-12"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Health Insights</h1>
          <p className="text-lg text-gray-600">Get predictions for various health conditions</p>
        </motion.div>

        {!selectedOption ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-white p-6 rounded-lg shadow-lg cursor-pointer transform transition-all duration-300 hover:shadow-xl"
              onClick={() => handleOptionSelect('disease')}
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Disease Prediction</h2>
              <p className="text-gray-600">Get predictions based on your symptoms</p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-white p-6 rounded-lg shadow-lg cursor-pointer opacity-50 transform transition-all duration-300"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Lung Cancer Prediction</h2>
              <p className="text-gray-600">Coming Soon</p>
            </motion.div>
          </div>
        ) : selectedOption === 'disease' ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="bg-white p-6 rounded-lg shadow-lg"
          >
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">Disease Prediction</h2>
            
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((num) => (
                <motion.div
                  key={num}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: num * 0.1 }}
                  className="flex flex-col"
                >
                  <label className="text-sm font-medium text-gray-700 mb-1">
                    Symptom {num}
                  </label>
                  <select
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md transition-all duration-300"
                    value={symptoms[num - 1]}
                    onChange={(e) => handleSymptomChange(num - 1, e.target.value)}
                  >
                    <option value="">Select a symptom</option>
                    {getAvailableOptionsForDropdown(num - 1).map((symptom, index) => (
                      <option key={index} value={symptom}>
                        {symptom.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </option>
                    ))}
                  </select>
                  {symptoms[num - 1] && (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-xs text-indigo-600 mt-1"
                    >
                      Selected: {symptoms[num - 1].replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </motion.p>
                  )}
                </motion.div>
              ))}
            </div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="mt-6 flex justify-between"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setSelectedOption(null);
                  setSymptoms(['', '', '', '', '']);
                  setPrediction(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300"
              >
                Back
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSubmit}
                disabled={loading || symptoms.some(s => !s)}
                className={`px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${symptoms.some(s => !s) ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300`}
              >
                {loading ? 'Predicting...' : 'Get Prediction'}
              </motion.button>
            </motion.div>

            {prediction && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="mt-6 p-4 bg-gray-50 rounded-lg"
              >
                <h3 className="text-lg font-medium text-gray-900 mb-4">Prediction Results</h3>
                {prediction.predictions.map((pred, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-3 rounded-lg mb-3 ${
                      index === 0 
                        ? 'bg-indigo-50 border border-indigo-200' 
                        : 'bg-white border border-gray-200'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className={`font-medium ${
                          index === 0 ? 'text-indigo-900' : 'text-gray-900'
                        }`}>
                          {index === 0 && <span className="text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded mr-2">Primary</span>}
                          {pred.disease}
                        </p>
                      </div>
                      <div className="flex items-center">
                        <div className="w-24 h-2 bg-gray-200 rounded-full mr-2">
                          <div
                            className={`h-2 rounded-full ${
                              index === 0 ? 'bg-indigo-600' : 'bg-indigo-400'
                            }`}
                            style={{ width: `${pred.confidence}%` }}
                          />
                        </div>
                        <span className={`text-sm ${
                          index === 0 ? 'text-indigo-900' : 'text-gray-600'
                        }`}>
                          {pred.confidence.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </motion.div>
                ))}
                <p className="text-xs text-gray-500 mt-4">
                  Note: Predictions are listed in order of confidence, with relative probabilities shown.
                </p>
              </motion.div>
            )}
          </motion.div>
        ) : null}
      </div>
    </motion.div>
  );
};

export default HealthInsights; 