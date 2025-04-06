import React from 'react'
import { assets } from '../assets/assets'

const Header = () => {
  return (
    <div className='flex flex-col md:flex-row flex-wrap bg-primary rounded-lg px-6 md:px-10 lg:px-20'>
      {/* Left side */}
      <div className='md:w-1/2 flex flex-col items-start justify-center gap-4 py-10 m-auto md:py-[10vw] md:mb-[30px]'>
        <p className='text-3xl md:text-4xl lg:text-5xl text-white font-semibold leading-tight lg:leading-tight'>
          Book Appointment <br />
          With Trusted Doctors
        </p>
        <p className='text-white text-sm font-light'>
          Simply browse through our extensive list of trusted doctors, <br className='hidden sm:block' />
          schedule your appointment hassle-free.
        </p>
        <a className='flex items-center gap-2 bg-white px-8 py-3 rounded-full text-gray-600 text-sm m-auto md:m-0 hover:scale-105 transition-all duration-300' href="#speciality">
          Book appointment <img className="w-3" src={assets.arrow_icon} alt="" />
        </a>
      </div>
      {/* Right side */}
      <div className='md:w-1/2 relative flex items-center justify-center'>
        <img 
          className='w-full md:w-[90%] h-auto rounded-lg transform transition-all duration-500 hover:scale-105' 
          src={assets.doctors_animate} 
          alt="Doctors illustration" 
        />
      </div>
    </div>
  )
}

export default Header