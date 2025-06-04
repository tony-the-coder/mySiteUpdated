import React, { useState } from 'react'

const ContactUs = () => {
  const [form, setForm] = useState({ name: '', email: '', message: '' })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission (e.g., send to API)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">Your Name</label>
        <input
          id="name"
          name="name"
          type="text"
          required
          className="mt-1 block w-full border-gray-300 rounded-md"
          value={form.name}
          onChange={handleChange}
        />
      </div>
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">Your Email</label>
        <input
          id="email"
          name="email"
          type="email"
          required
          className="mt-1 block w-full border-gray-300 rounded-md"
          value={form.email}
          onChange={handleChange}
        />
      </div>
      <div>
        <label htmlFor="message" className="block text-sm font-medium text-gray-700">Message</label>
        <textarea
          id="message"
          name="message"
          required
          className="mt-1 block w-full border-gray-300 rounded-md"
          value={form.message}
          onChange={handleChange}
        />
      </div>
      <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Send</button>
    </form>
  )
}

export default ContactUs