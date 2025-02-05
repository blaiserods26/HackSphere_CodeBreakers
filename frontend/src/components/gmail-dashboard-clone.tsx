"use client"
import { useState } from 'react';
import { Mail, Star, Inbox, Clock, Send, FileText, Menu, Search, Settings, HelpCircle, Grid, User } from 'lucide-react';

export default function GmailDashboard() {
  const [emails] = useState([
    {
      id: 1,
      sender: "contineo.crce",
      subject: "[SAFE] Email Security Analysis - Score: 67/100",
      preview: "Dear Sender, Thank you for reaching out! We have performed a security analys...",
      time: "14:41",
      isStarred: false,
      isRead: false
    },
    {
      id: 2,
      sender: "contineo.crce",
      subject: "Thank You for Your Email!",
      preview: "Dear Sender, Thank you for reaching out! We have received your message and performed a security...",
      time: "14:40",
      isStarred: false,
      isRead: true
    },
    {
      id: 3,
      sender: "Zomato",
      subject: "chaichaichaichaichaichaichaichai",
      preview: "---------- Forwarded message ---------- From: Zomato <noreply@mailers.zomato.com> Da...",
      time: "12:31",
      isStarred: false,
      isRead: false
    },
    {
      id: 4,
      sender: "Coding",
      subject: "Update: Submit your application to complete your certification",
      preview: "---------- Forwarded message ---------- From: Coding Ninjas ...",
      time: "12:15",
      isStarred: false,
      isRead: true
    },
    {
      id: 5,
      sender: "Contineo Support",
      subject: "Hello Ross",
      preview: "Ross",
      time: "11:43",
      isStarred: false,
      isRead: false
    }
  ]);

  return (
    <div className="h-screen flex flex-col">

      <div className="flex flex-1">
        {/* Sidebar */}
        <div className="w-64 p-4 border-r border-gray-200">
          <button className="flex items-center space-x-3 px-6 py-3 rounded-2xl bg-blue-100 text-blue-600 hover:shadow-md transition-all mb-4">
            <FileText className="w-5 h-5" />
            <span>Compose</span>
          </button>

          <div className="space-y-1">
            <button className="flex items-center space-x-3 px-6 py-2 rounded-r-full w-full hover:bg-gray-100 bg-blue-50 text-blue-600">
              <Inbox className="w-5 h-5" />
              <span>Safe</span>
            </button>
            <button className="flex items-center space-x-3 px-6 py-2 rounded-r-full w-full hover:bg-gray-100">
              <Star className="w-5 h-5 text-gray-600" />
              <span>Unsafe</span>
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Email List Header */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200">
            <div className="flex items-center space-x-4">
              <input type="checkbox" className="rounded border-gray-300" />
              <button className="p-2 hover:bg-gray-100 rounded-full">
                <Mail className="w-5 h-5 text-gray-600" />
              </button>
            </div>
            <div className="text-sm text-gray-600">1-50 of 2,893</div>
          </div>

          {/* Email List */}
          <div className="flex-1 overflow-y-auto">
            {emails.map((email) => (
              <div
                key={email.id}
                className={`flex items-center px-4 py-2 hover:shadow-md cursor-pointer border-b border-gray-100 ${
                  email.isRead ? 'bg-white' : 'bg-gray-50 font-semibold'
                }`}
              >
                <input type="checkbox" className="mr-4 rounded border-gray-300" />
                <Star
                  className={`w-5 h-5 mr-4 ${
                    email.isStarred ? 'text-yellow-400' : 'text-gray-400'
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center">
                    <span className="w-48 truncate">{email.sender}</span>
                    <span className="flex-1 truncate">{email.subject}</span>
                    <span className="ml-4 text-sm text-gray-600 whitespace-nowrap">
                      {email.time}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 truncate">{email.preview}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
