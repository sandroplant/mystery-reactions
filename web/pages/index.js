import React from 'react';

const IndexPage = () => {
  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px', textAlign: 'center' }}>
      <section style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '3em', margin: '0.5em 0' }}>Welcome to Our Service</h1>
        <p style={{ fontSize: '1.2em', color: '#666' }}>Join our waitlist to stay updated!</p>
      </section>
      <section>
        <form style={{ display: 'inline-block', textAlign: 'left' }}>
          <div style={{ marginBottom: '10px' }}>
            <label htmlFor="email" style={{ display: 'block', marginBottom: '5px' }}>Email:</label>
            <input type="email" id="email" name="email" style={{ padding: '10px', width: '100%', boxSizing: 'border-box' }} required />
          </div>
          <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#0070f3', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
            Join Waitlist
          </button>
        </form>
      </section>
    </div>
  );
};

export default IndexPage;
