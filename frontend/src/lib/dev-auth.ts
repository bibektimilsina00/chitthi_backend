import { tokenManager } from "@/lib/token-manager";

// For development/testing purposes, set the provided auth token
if (typeof window !== "undefined") {
  const token =
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTgwMjE1MzQsInN1YiI6IjE5NzEyMjJiLTg3OTgtNGQyYi1hNGIwLWZmZjAzNWFjODQ0YiJ9.Oeer0wyTEpNtQr6GyjDvUtXh0t4F2GYXhldvYMwHTqQ";
  tokenManager.setToken(token);
  console.log("Auth token set for development");
}
