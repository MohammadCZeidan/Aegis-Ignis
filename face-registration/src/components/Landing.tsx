import { Shield, Building2, Video, AlertTriangle, Lock, Users, TrendingUp, Bell, Sparkles } from 'lucide-react';
import logo from '../assets/aegis-logo.png';

interface LandingProps {
  onGetStarted: () => void;
}

// Logo component with animation
const AnimatedLogo = ({ className }: { className?: string }) => (
  <div className={`transition-transform hover:scale-110 ${className}`}>
    <img src={logo} alt="Aegis Ignis" className="w-full h-full object-contain drop-shadow-2xl" />
  </div>
);

export function Landing({ onGetStarted }: LandingProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Navigation */}
      <nav className="border-b border-white/10 bg-slate-900/30 backdrop-blur-xl relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <div className="flex items-center gap-3">
              <AnimatedLogo className="h-16 w-16 lg:h-20 lg:w-20" />
              <div>
                <h1 className="text-lg lg:text-2xl font-bold bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-400 bg-clip-text text-transparent">
                  Aegis Ignis
                </h1>
                <p className="text-xs text-slate-400 hidden sm:block">Face Registration</p>
              </div>
            </div>
            <button 
              onClick={onGetStarted} 
              className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white px-6 py-2 lg:px-8 lg:py-2.5 rounded-lg font-semibold transition-all shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 flex items-center gap-2"
            >
              <Sparkles className="h-4 w-4" />
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-24 relative z-10">
        <div className="text-center mb-16">
          
          {/* Logo in Hero with Glow */}
          <div className="mb-4 flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-3xl opacity-30 animate-pulse"></div>
              <AnimatedLogo className="h-48 w-48 lg:h-64 lg:w-64 relative" />
            </div>
          </div>
          
          <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold mb-6">
            <span className="bg-gradient-to-r from-white via-blue-100 to-white bg-clip-text text-transparent">
              Employee Face Registration
            </span>
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent animate-gradient">
              Secure & Intelligent
            </span>
          </h1>
          
          <p className="text-lg lg:text-xl text-slate-300 max-w-3xl mx-auto mb-8 leading-relaxed">
            Register employee faces for advanced security and access control. <span className="text-cyan-400 font-semibold">Aegis Ignis</span> uses cutting-edge AI technology
            for accurate facial recognition, ensuring secure building access and comprehensive attendance tracking.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button 
              onClick={onGetStarted} 
              className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white h-12 lg:h-14 px-8 text-base lg:text-lg w-full sm:w-auto rounded-lg font-semibold transition-all shadow-2xl shadow-blue-500/40 hover:shadow-blue-500/60 hover:scale-105 flex items-center justify-center gap-2"
            >
              <Sparkles className="h-5 w-5" />
              Start Registration
            </button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-16">
          <div className="p-6 bg-slate-800/50 border border-slate-700 backdrop-blur-sm rounded-xl">
            <div className="p-3 bg-blue-600/20 rounded-lg w-fit mb-4">
              <Video className="h-6 w-6 lg:h-8 lg:w-8 text-blue-400" />
            </div>
            <h3 className="text-lg lg:text-xl text-white mb-2 font-semibold">Live Cameras</h3>
            <p className="text-slate-400 text-sm lg:text-base">
              Monitor all camera feeds in real-time with AI-powered detection and tracking.
            </p>
          </div>

          <div className="p-6 bg-slate-800/50 border border-slate-700 backdrop-blur-sm rounded-xl">
            <div className="p-3 bg-orange-600/20 rounded-lg w-fit mb-4">
              <AlertTriangle className="h-6 w-6 lg:h-8 lg:w-8 text-orange-400" />
            </div>
            <h3 className="text-lg lg:text-xl text-white mb-2 font-semibold">Fire Detection</h3>
            <p className="text-slate-400 text-sm lg:text-base">
              Advanced smoke and fire detection with instant emergency alerts.
            </p>
          </div>

          <div className="p-6 bg-slate-800/50 border border-slate-700 backdrop-blur-sm rounded-xl">
            <div className="p-3 bg-green-600/20 rounded-lg w-fit mb-4">
              <Users className="h-6 w-6 lg:h-8 lg:w-8 text-green-400" />
            </div>
            <h3 className="text-lg lg:text-xl text-white mb-2 font-semibold">Occupancy Tracking</h3>
            <p className="text-slate-400 text-sm lg:text-base">
              Track building occupancy across all floors with detailed analytics.
            </p>
          </div>

          <div className="p-6 bg-slate-800/50 border border-slate-700 backdrop-blur-sm rounded-xl">
            <div className="p-3 bg-purple-600/20 rounded-lg w-fit mb-4">
              <Building2 className="h-6 w-6 lg:h-8 lg:w-8 text-purple-400" />
            </div>
            <h3 className="text-lg lg:text-xl text-white mb-2 font-semibold">Floor Management</h3>
            <p className="text-slate-400 text-sm lg:text-base">
              Comprehensive floor-by-floor monitoring and control system.
            </p>
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-8 mb-16">
          <div className="text-center p-6 bg-slate-800/30 rounded-lg border border-slate-700">
            <div className="flex items-center justify-center gap-2 mb-2">
              <TrendingUp className="h-5 w-5 text-green-400" />
              <p className="text-3xl lg:text-4xl text-white font-bold">99.9%</p>
            </div>
            <p className="text-slate-400 text-sm lg:text-base">Uptime</p>
          </div>
          
          <div className="text-center p-6 bg-slate-800/30 rounded-lg border border-slate-700">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Video className="h-5 w-5 text-blue-400" />
              <p className="text-3xl lg:text-4xl text-white font-bold">50+</p>
            </div>
            <p className="text-slate-400 text-sm lg:text-base">Cameras</p>
          </div>
          
          <div className="text-center p-6 bg-slate-800/30 rounded-lg border border-slate-700">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Building2 className="h-5 w-5 text-purple-400" />
              <p className="text-3xl lg:text-4xl text-white font-bold">4</p>
            </div>
            <p className="text-slate-400 text-sm lg:text-base">Floors</p>
          </div>
          
          <div className="text-center p-6 bg-slate-800/30 rounded-lg border border-slate-700">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Bell className="h-5 w-5 text-orange-400" />
              <p className="text-3xl lg:text-4xl text-white font-bold">&lt;1s</p>
            </div>
            <p className="text-slate-400 text-sm lg:text-base">Alert Time</p>
          </div>
        </div>

        {/* What We Do Section */}
        <div className="mb-16 bg-slate-800/30 border border-slate-700 rounded-2xl p-8 lg:p-12">
          <div className="text-center mb-10">
            <h2 className="text-3xl lg:text-4xl text-white mb-4 font-bold">What Does Aegis Ignis Do?</h2>
            <p className="text-slate-300 text-base lg:text-lg max-w-3xl mx-auto">
              Aegis Ignis is an all-in-one security management platform designed to protect commercial buildings, 
              corporate offices, and multi-floor facilities with cutting-edge technology.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
            {/* Purpose Card */}
            <div className="p-6 lg:p-8 bg-slate-900/50 border border-slate-600 rounded-xl">
              <h3 className="text-xl lg:text-2xl text-white mb-4 flex items-center gap-3 font-semibold">
                <Shield className="h-6 w-6 text-blue-400" />
                Our Purpose
              </h3>
              <p className="text-slate-300 mb-4">
                We built Aegis Ignis to solve the complex challenge of managing modern building security. 
                Traditional security systems are fragmented, difficult to monitor, and slow to respond to emergencies.
              </p>
              <p className="text-slate-300">
                Our mission is to provide building managers, security teams, and facility operators with a unified platform 
                that delivers instant visibility, intelligent alerts, and rapid emergency response—keeping people safe and assets protected.
              </p>
            </div>

            {/* How It Works Card */}
            <div className="p-6 lg:p-8 bg-slate-900/50 border border-slate-600 rounded-xl">
              <h3 className="text-xl lg:text-2xl text-white mb-4 flex items-center gap-3 font-semibold">
                <Video className="h-6 w-6 text-blue-400" />
                How It Works
              </h3>
              <ul className="space-y-3 text-slate-300">
                <li className="flex items-start gap-3">
                  <span className="text-blue-400 mt-1">•</span>
                  <span><strong className="text-white">Real-Time Monitoring:</strong> Track all cameras, sensors, and detectors from one dashboard</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-blue-400 mt-1">•</span>
                  <span><strong className="text-white">AI Detection:</strong> Automatically identify fire, smoke, and security threats</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-blue-400 mt-1">•</span>
                  <span><strong className="text-white">Instant Alerts:</strong> Receive notifications within seconds of incident detection</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-blue-400 mt-1">•</span>
                  <span><strong className="text-white">Mobile Access:</strong> Monitor and respond from anywhere, on any device</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Key Benefits */}
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-600/10 border border-blue-500/30 rounded-lg">
              <Lock className="h-8 w-8 text-blue-400 mx-auto mb-2" />
              <h4 className="text-white mb-1 font-semibold">Enhanced Safety</h4>
              <p className="text-sm text-slate-400">Protect occupants with 24/7 surveillance and fire detection</p>
            </div>
            <div className="text-center p-4 bg-green-600/10 border border-green-500/30 rounded-lg">
              <TrendingUp className="h-8 w-8 text-green-400 mx-auto mb-2" />
              <h4 className="text-white mb-1 font-semibold">Operational Efficiency</h4>
              <p className="text-sm text-slate-400">Manage all security systems from a single interface</p>
            </div>
            <div className="text-center p-4 bg-orange-600/10 border border-orange-500/30 rounded-lg">
              <Bell className="h-8 w-8 text-orange-400 mx-auto mb-2" />
              <h4 className="text-white mb-1 font-semibold">Rapid Response</h4>
              <p className="text-sm text-slate-400">React to emergencies faster with instant notifications</p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-8 lg:p-12">
          <h2 className="text-2xl lg:text-4xl text-white mb-4 font-bold">
            Ready to Secure Your Building?
          </h2>
          <p className="text-blue-100 text-base lg:text-lg mb-6 max-w-2xl mx-auto">
            Get started with Aegis Ignis today and experience next-generation building security management.
          </p>
          <button 
            onClick={onGetStarted}
            className="bg-white text-blue-600 hover:bg-slate-100 h-12 lg:h-14 px-8 text-base lg:text-lg rounded-lg font-semibold transition-colors"
          >
            Access Dashboard Now
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-slate-900/50 backdrop-blur-sm mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-slate-400 text-sm">
            <p>&copy; 2026 Aegis Ignis. All rights reserved.</p>
            <p className="mt-2">Enterprise Building Security & Fire Detection System</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
