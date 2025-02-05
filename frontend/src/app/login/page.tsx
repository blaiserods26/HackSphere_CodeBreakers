"use client";
import React, { useEffect, useState } from 'react';
import { getAuth, signInWithPopup, GoogleAuthProvider, User, onAuthStateChanged } from 'firebase/auth';
import { auth, db } from '@/lib/firebase'; // Import the initialized Firebase app
import { Button, Card } from 'flowbite-react';
import { useRouter } from 'next/navigation';

const provider = new GoogleAuthProvider();

const LoginPage = () => {
  const [userAuth, setUserAuth] = useState<User | null>(null);
  const router = useRouter();

  useEffect(() => {
    const listen = onAuthStateChanged(auth, (user: User | null) => {
      if (user) {
        setUserAuth(user);
        router.push('/home'); // Redirect to /home if already logged in
      } else {
        setUserAuth(null);
      }
    });
    return () => {
      listen();
    };
  }, [router]);

  const handleGoogleLogin = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      // Handle successful login
      console.log(result.user);
   
    } catch (error) {
      // Handle Errors here.
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FFFFFF] to-[#ADEBFF] dark:from-[#00171F] dark:to-[#003459] flex items-center justify-center">
      <Card className="max-w-md w-full p-8 bg-[#FFFFFF]/50 dark:bg-[#00171F]/50 backdrop-blur-sm">
        <h1 className="text-4xl font-bold text-center text-[#003459] dark:text-[#FFFFFF] mb-8">Login</h1>
        <Button 
          className="w-full bg-[#003459] hover:bg-[#003459]/90 text-[#FFFFFF] dark:bg-[#ADEBFF] dark:hover:bg-[#ADEBFF]/90 dark:text-[#003459] px-8 py-4 text-lg"
          onClick={handleGoogleLogin}
        >
          Login with Google
        </Button>
      </Card>
    </div>
  );
};

export default LoginPage;
