import React from 'react'
import { assets } from '../assets/assets'

const Footer = () => {
    return (
        <div className='md:mx-10 '>
            <div className='flex flex-col sm:grid grid-cols-[3fr_1fr_1fr] gap-14 my-10 mt-40 text-sm'>
                {/* left section */}
                <div>
                    <img className='mb-5 w-40 ' src={assets.logo} alt="" />
                    <p className='w-full md:w:2/3 text-gray-600 leading-6'>HealthMate is on a mission to revolutionize healthcare through technology. With innovation at our core, we strive to build smart, accessible, and impactful solutions for a healthier future. Join us on our journey to transform lives, one innovation at a time.</p>
                </div>
                {/* Center section  */}
                <div>
                    <p className='textxl font-medium  mb-5'>COMPANY</p>
                    <ul className='flex flex-col gap-2 text-gray-600'>
                        <li>Home</li>
                        <li>About us</li>
                        <li>Contact us</li>
                        <li>Privacy policy</li>
                    </ul>
                </div>
                {/* right section */}
                <div>
                    <p className='textxl font-medium  mb-5'>GET IN TOUCH</p>
                    <ul className='flex flex-col gap-2 text-gray-600'>
                        <li>+91 93273 52258, +91 82006 37718</li>
                        <li>20220702028@karnavatiuniversity.edu.in, 20220702029@karnavatiuniversity.edu.in</li>
                    </ul>
                </div>
            </div>
            {/* copy right text */}
            <div>
                <hr />
            <p className='py-5 text-sm text-center'>Copyright © 2025 HealthMate - All Right Reserved.</p>
            </div>
        </div>
    )
}

export default Footer