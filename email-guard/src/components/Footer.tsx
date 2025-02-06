"use client";
const Footer = () => {
  return (
    <div className="bg-gray-800 text-white p-4 md:flex md:justify-between">
      <div className="mb-4 md:mb-0">
        <h2 className="text-lg font-bold">Company Name</h2>
        <p className="text-sm">© 2023 Company Name. All rights reserved.</p>
      </div>
      <div className="flex space-x-4">
        <a href="#" className="text-sm hover:underline">Privacy Policy</a>
        <a href="#" className="text-sm hover:underline">Terms of Service</a>
        <a href="#" className="text-sm hover:underline">Contact Us</a>
      </div>
    </div>
  );
};
export default Footer;
