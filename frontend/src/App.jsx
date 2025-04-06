import React from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Home from './pages/Home'
import About from './pages/About'
import Doctors from './pages/Doctors'
import Login from './pages/Login'
import Contact from './pages/Contact'
import MyProfile from './pages/MyProfile'
import MyAppointments from './pages/MyAppointments'
import Appointment from './pages/Appointment'
import HealthInsights from './pages/HealthInsights'
import ProtectedRoute from './components/ProtectedRoute'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const App = () => {
  const location = useLocation();

  return (
    <div className='mx-4 sm:mx-[10%]'>
      <ToastContainer />
      <Navbar />
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Home />} />
          <Route path='/doctors' element={<Doctors />} />
          <Route path='/doctors/:speciality' element={<Doctors />} />
          <Route path='/login' element={<Login />} />
          <Route path='/about' element={<About />} />
          <Route path='/contact' element={<Contact />} />
          <Route path='/my-profile' element={
            <ProtectedRoute>
              <MyProfile />
            </ProtectedRoute>
          } />
          <Route path='/my-appointments' element={
            <ProtectedRoute>
              <MyAppointments />
            </ProtectedRoute>
          } />
          <Route path='/appointment/:docId' element={
            <ProtectedRoute>
              <Appointment />
            </ProtectedRoute>
          } />
          <Route path='/health-insights' element={
            <ProtectedRoute>
              <HealthInsights />
            </ProtectedRoute>
          } />
        </Routes>
      </AnimatePresence>
      <Footer />
    </div>
  )
}

export default App