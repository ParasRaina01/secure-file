import React from 'react'
import { Link } from 'react-router-dom'
import { Shield, Lock, Share2, Key, Users, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'

const features = [
  {
    icon: Shield,
    title: 'End-to-End Encryption',
    description: 'Your files are encrypted before they leave your device, ensuring maximum security.',
  },
  {
    icon: Lock,
    title: 'Two-Factor Authentication',
    description: 'Add an extra layer of security to your account with 2FA.',
  },
  {
    icon: Share2,
    title: 'Secure File Sharing',
    description: 'Share files securely with other users or via time-limited links.',
  },
  {
    icon: Key,
    title: 'Access Control',
    description: 'Fine-grained control over who can access your files and for how long.',
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Work together securely with your team members.',
  },
  {
    icon: Clock,
    title: 'Expiring Links',
    description: 'Create shareable links that automatically expire after a set time.',
  },
]

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="h-6 w-6" />
            <span className="font-bold">SecureShare</span>
          </div>
          <nav className="flex items-center space-x-4">
            <Link to="/login">
              <Button variant="ghost">Sign in</Button>
            </Link>
            <Link to="/register">
              <Button>Get Started</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container py-24 sm:py-32">
        <div className="flex flex-col items-center text-center space-y-8">
          <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
            Share Files Securely<br />
            <span className="text-primary">With Confidence</span>
          </h1>
          <p className="max-w-[600px] text-muted-foreground text-lg sm:text-xl">
            SecureShare provides end-to-end encrypted file sharing with advanced security features.
            Keep your sensitive data protected while collaborating with others.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link to="/register">
              <Button size="lg" className="w-full sm:w-auto">
                Start Sharing Securely
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                Sign in to Your Account
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container py-24 sm:py-32">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div
                key={index}
                className="flex flex-col items-center text-center space-y-4 p-6 rounded-lg border bg-card"
              >
                <div className="p-3 rounded-full bg-primary/10">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t">
        <div className="container py-24 sm:py-32">
          <div className="flex flex-col items-center text-center space-y-8">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
              Ready to Share Securely?
            </h2>
            <p className="max-w-[600px] text-muted-foreground text-lg">
              Join thousands of users who trust SecureShare for their secure file sharing needs.
              Get started today with our free plan.
            </p>
            <Link to="/register">
              <Button size="lg">Create Your Free Account</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t">
        <div className="container py-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span className="font-semibold">SecureShare</span>
          </div>
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} SecureShare. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Landing 