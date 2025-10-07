import Head from 'next/head';

export default function Home() {
  return (
    <div>
      <Head>
        <title>Landing Page</title>
        <meta name="description" content="Join our waitlist" />
      </Head>
      <main>
        <section style={{ padding: '50px', textAlign: 'center' }}>
          <h1>Welcome to Our Landing Page</h1>
          <p>Join our waitlist to stay updated!</p>
          <form>
            <input type="email" placeholder="Enter your email" required />
            <button type="submit">Join Waitlist</button>
          </form>
        </section>
      </main>
    </div>
  );
}