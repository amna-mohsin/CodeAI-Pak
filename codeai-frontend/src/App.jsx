import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Upload, CheckCircle, AlertTriangle, TrendingUp, Code, Zap, Shield, Menu, X, Mail, MapPin, Phone, Lightbulb, BookOpen, Sparkles } from 'lucide-react';
import AuthPage from './AuthPage';
import Dashboard from './Dashboard';

// ============================================
// SCROLL ANIMATIONS HOOK
// ============================================
const useScrollAnimation = () => {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return scrollY;
};

// ============================================
// SCROLL PROGRESS BAR
// ============================================
const ScrollProgressBar = () => {
  const scrollY = useScrollAnimation();
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const calculateScrollProgress = () => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollTop = window.scrollY;
      const trackLength = documentHeight - windowHeight;
      const progress = (scrollTop / trackLength) * 100;
      setScrollProgress(progress);
    };

    calculateScrollProgress();
    window.addEventListener('scroll', calculateScrollProgress, { passive: true });
    return () => window.removeEventListener('scroll', calculateScrollProgress);
  }, []);

  return (
    <div style={styles.scrollProgressContainer}>
      <div 
        style={{
          ...styles.scrollProgressBar,
          width: `${scrollProgress}%`,
        }}
      />
    </div>
  );
};

// ============================================
// SMOOTH SCROLL FUNCTION
// ============================================
const smoothScrollTo = (elementId) => {
  const element = document.getElementById(elementId);
  if (element) {
    element.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
  }
};

// ============================================
// NAVBAR COMPONENT (FIXED & MORPHING)
// ============================================
const Navbar = ({ isAuthenticated, onLogout }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const onScroll = () => setIsScrolled(window.scrollY > 50);
    const onResize = () => setIsMobile(window.innerWidth <= 768);

    onScroll();
    onResize();

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onResize);

    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onResize);
    };
  }, []);

  const handleNavClick = (id) => {
    navigate('/');
    setTimeout(() => smoothScrollTo(id), 100);
    setMobileMenuOpen(false);
  };

  const handleTryDemo = () => {
    navigate('/auth');
    setMobileMenuOpen(false);
  };

const handleLogoutClick = async () => {
    try {
      await fetch('http://localhost:5000/api/logout', {
        method: 'POST',
        credentials: 'include'
      });
      // Use window.location for a full page reload to clear all state
      window.location.href = '/';
    } catch (err) {
      console.error('Logout error:', err);
      // Even on error, redirect
      window.location.href = '/';
    }
  };
  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        zIndex: 1000,
        display: 'flex',
        justifyContent: 'center',
        background: 'transparent',
        pointerEvents: 'none',
      }}
    >
      <ScrollProgressBar />

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          width: isMobile ? '100%' : isScrolled ? '1100px' : '100%',
          maxWidth: '100%',
          marginTop: isScrolled ? '18px' : '0px',
          padding: isMobile ? '14px 20px' : isScrolled ? '14px 36px' : '22px 60px',
          borderRadius: isScrolled ? '999px' : '0px',
          background: 'rgba(10, 10, 15, 0.92)',
          backdropFilter: 'blur(18px)',
          WebkitBackdropFilter: 'blur(18px)',
          border: isScrolled ? '1px solid rgba(139, 92, 246, 0.4)' : '1px solid rgba(139, 92, 246, 0.2)',
          boxShadow: isScrolled ? '0 12px 40px rgba(0,0,0,0.6)' : 'none',
          overflow: 'hidden',
          transition: 'all 0.45s cubic-bezier(0.16, 1, 0.3, 1)',
          pointerEvents: 'auto',
        }}
      >
        <div
          onClick={() => handleNavClick('home')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            marginRight: !isMobile && isScrolled ? '48px' : '0',
          }}
        >
          <Code size={isScrolled ? 24 : 28} style={styles.brandIcon} />
          <span style={{ ...styles.brandText, fontSize: '18px' }}>
            CodeAI Pakistan
          </span>
        </div>

        {!isMobile && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: isScrolled ? '32px' : '36px',
              transition: 'gap 0.3s ease',
            }}
          >
            <a onClick={() => handleNavClick('home')} style={styles.navLink}>Home</a>
            <a onClick={() => handleNavClick('about')} style={styles.navLink}>About</a>
            <a onClick={() => handleNavClick('blog')} style={styles.navLink}>Blog</a>
            <a onClick={() => handleNavClick('contact')} style={styles.navLink}>Contact</a>

            {isAuthenticated ? (
              <button onClick={handleLogoutClick} style={styles.logoutBtn}>
                Logout
              </button>
            ) : (
              <button onClick={handleTryDemo} style={styles.tryDemoBtn}>
                Try Demo
              </button>
            )}
          </div>
        )}

        {isMobile && (
          <button
            style={styles.mobileMenuBtn}
            onClick={() => setMobileMenuOpen((p) => !p)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        )}
      </div>

      {isMobile && mobileMenuOpen && (
        <div
          style={{
            ...styles.mobileMenu,
            marginTop: '12px',
            width: 'calc(100% - 32px)',
            borderRadius: '20px',
          }}
        >
          <a onClick={() => handleNavClick('home')} style={styles.mobileLink}>Home</a>
          <a onClick={() => handleNavClick('about')} style={styles.mobileLink}>About</a>
          <a onClick={() => handleNavClick('blog')} style={styles.mobileLink}>Blog</a>
          <a onClick={() => handleNavClick('contact')} style={styles.mobileLink}>Contact</a>

          {isAuthenticated ? (
            <button onClick={handleLogoutClick} style={styles.mobileTryDemoBtn}>
              Logout
            </button>
          ) : (
            <button onClick={handleTryDemo} style={styles.mobileTryDemoBtn}>
              Try Demo
            </button>
          )}
        </div>
      )}
    </nav>
  );
};

// ============================================
// ANIMATED SECTION COMPONENT
// ============================================
const AnimatedSection = ({ children, id, delay = 0 }) => {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current);
      }
    };
  }, []);

  return (
    <div
      ref={sectionRef}
      id={id}
      style={{
        ...styles.section,
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(40px)',
        transition: `all 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${delay}ms`,
      }}
    >
      {children}
    </div>
  );
};

// ============================================
// HOME SECTION
// ============================================
const HomeSection = () => {
  const scrollY = useScrollAnimation();
  const parallaxY = scrollY * 0.4;
  const rotateAmount = Math.min(scrollY * 0.03, 8);
  const navigate = useNavigate();

  return (
    <AnimatedSection id="home">
      <div style={styles.heroSection}>
        <div 
          style={{
            ...styles.glowOrb,
            transform: `translateX(-50%) translateY(${parallaxY}px) rotate(${rotateAmount}deg)`,
          }}
        />
        <h1 
          style={{
            ...styles.heroTitle,
            transform: `translateY(${parallaxY * -0.4}px)`,
          }}
        >
          AI-Powered Code Quality
          <br />
          <span style={styles.heroGradient}>At Lightning Speed</span>
        </h1>
        <p 
          style={{
            ...styles.heroSubtitle,
            transform: `translateY(${parallaxY * -0.25}px)`,
          }}
        >
          Detect bugs, analyze complexity, and improve code quality instantly with advanced AI technology
        </p>
        <button 
          onClick={() => navigate('/auth')} 
          style={{
            ...styles.heroButton,
            transform: `translateY(${parallaxY * -0.1}px)`,
          }}
        >
          <Zap size={20} style={{ marginRight: '8px' }} />
          Start Analyzing Now
        </button>

        <div style={styles.featureGrid}>
          <FeatureCard
            icon={<Shield size={32} />}
            title="Bug Detection"
            description="AI identifies vulnerabilities and bugs before they reach production"
            delay={0}
          />
          <FeatureCard
            icon={<TrendingUp size={32} />}
            title="Quality Metrics"
            description="Real-time code quality scores and actionable improvement suggestions"
            delay={100}
          />
          <FeatureCard
            icon={<Zap size={32} />}
            title="Instant Analysis"
            description="Get comprehensive reports in seconds, not hours"
            delay={200}
          />
        </div>
      </div>
    </AnimatedSection>
  );
};

const FeatureCard = ({ icon, title, description, delay }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      style={{
        ...styles.featureCard,
        transform: isHovered ? 'translateY(-15px) scale(1.05) rotateX(5deg)' : 'translateY(0) scale(1) rotateX(0deg)',
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        boxShadow: isHovered 
          ? '0 20px 60px rgba(139, 92, 246, 0.3), 0 0 0 1px rgba(139, 92, 246, 0.5)' 
          : '0 8px 32px rgba(139, 92, 246, 0.1)',
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div style={styles.featureIcon}>{icon}</div>
      <h3 style={styles.featureTitle}>{title}</h3>
      <p style={styles.featureDescription}>{description}</p>
    </div>
  );
};

// ============================================
// OTHER SECTIONS (About, Blog, Contact)
// ============================================
const AboutSection = () => {
  return (
    <AnimatedSection id="about" delay={100}>
      <div style={styles.aboutSection}>
        <div style={styles.aboutContent}>
          <div style={styles.aboutHeader}>
            <Sparkles size={48} style={{ color: '#8b5cf6', marginBottom: '24px' }} />
            <h2 style={styles.sectionTitle}>About CodeAI Pakistan</h2>
            <p style={styles.sectionSubtitle}>
              Revolutionizing software development with cutting-edge AI technology
            </p>
          </div>

          <div style={styles.aboutGrid}>
            <div style={styles.aboutCard}>
              <Lightbulb size={32} style={{ color: '#ec4899', marginBottom: '16px' }} />
              <h3 style={styles.aboutCardTitle}>Our Mission</h3>
              <p style={styles.aboutCardText}>
                To empower developers across Pakistan with world-class AI-powered code analysis tools, 
                making high-quality software development accessible to everyone.
              </p>
            </div>

            <div style={styles.aboutCard}>
              <TrendingUp size={32} style={{ color: '#10b981', marginBottom: '16px' }} />
              <h3 style={styles.aboutCardTitle}>Our Vision</h3>
              <p style={styles.aboutCardText}>
                To become the leading AI code quality platform in South Asia, helping thousands of 
                developers write better, more secure code every day.
              </p>
            </div>

            <div style={styles.aboutCard}>
              <Shield size={32} style={{ color: '#f59e0b', marginBottom: '16px' }} />
              <h3 style={styles.aboutCardTitle}>Our Technology</h3>
              <p style={styles.aboutCardText}>
                Built on advanced machine learning models trained on millions of lines of code, 
                providing real-time insights and suggestions tailored to your projects.
              </p>
            </div>
          </div>

          <div style={styles.statsSection}>
            <div style={styles.statItem}>
              <h3 style={styles.statNumber}>50K+</h3>
              <p style={styles.statLabel}>Lines Analyzed</p>
            </div>
            <div style={styles.statItem}>
              <h3 style={styles.statNumber}>1000+</h3>
              <p style={styles.statLabel}>Bugs Detected</p>
            </div>
            <div style={styles.statItem}>
              <h3 style={styles.statNumber}>95%</h3>
              <p style={styles.statLabel}>Accuracy Rate</p>
            </div>
            <div style={styles.statItem}>
              <h3 style={styles.statNumber}>24/7</h3>
              <p style={styles.statLabel}>Support</p>
            </div>
          </div>
        </div>
      </div>
    </AnimatedSection>
  );
};

const BlogSection = () => {
  const blogPosts = [
    {
      title: "The Future of AI in Software Development",
      excerpt: "Exploring how artificial intelligence is transforming the way we write and maintain code.",
      date: "Dec 10, 2024",
      icon: <Code size={24} />
    },
    {
      title: "10 Common Coding Mistakes and How to Avoid Them",
      excerpt: "Learn about the most frequent errors developers make and best practices to prevent them.",
      date: "Dec 5, 2024",
      icon: <AlertTriangle size={24} />
    },
    {
      title: "Building Secure Applications in 2024",
      excerpt: "A comprehensive guide to modern security practices and vulnerability prevention.",
      date: "Nov 28, 2024",
      icon: <Shield size={24} />
    }
  ];

  return (
    <AnimatedSection id="blog" delay={150}>
      <div style={styles.blogSection}>
        <div style={styles.blogHeader}>
          <BookOpen size={48} style={{ color: '#8b5cf6', marginBottom: '24px' }} />
          <h2 style={styles.sectionTitle}>Latest from Our Blog</h2>
          <p style={styles.sectionSubtitle}>
            Insights, tutorials, and updates from the CodeAI team
          </p>
        </div>

        <div style={styles.blogGrid}>
          {blogPosts.map((post, index) => (
            <BlogCard key={index} post={post} delay={index * 100} />
          ))}
        </div>
      </div>
    </AnimatedSection>
  );
};

const BlogCard = ({ post, delay }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      style={{
        ...styles.blogCard,
        transform: isHovered ? 'translateY(-10px) rotateX(5deg)' : 'translateY(0) rotateX(0deg)',
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div style={styles.blogCardIcon}>{post.icon}</div>
      <div style={styles.blogCardDate}>{post.date}</div>
      <h3 style={styles.blogCardTitle}>{post.title}</h3>
      <p style={styles.blogCardExcerpt}>{post.excerpt}</p>
      <button style={styles.blogCardButton}>Read More →</button>
    </div>
  );
};

const ContactSection = () => {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Message sent! We\'ll get back to you soon.');
    setFormData({ name: '', email: '', message: '' });
  };

  return (
    <AnimatedSection id="contact" delay={200}>
      <div style={styles.contactSection}>
        <div style={styles.contactHeader}>
          <Mail size={48} style={{ color: '#8b5cf6', marginBottom: '24px' }} />
          <h2 style={styles.sectionTitle}>Get In Touch</h2>
          <p style={styles.sectionSubtitle}>
            Have questions? We'd love to hear from you.
          </p>
        </div>

        <div style={styles.contactContent}>
          <div style={styles.contactInfo}>
            <div style={styles.contactInfoItem}>
              <MapPin size={24} style={{ color: '#8b5cf6' }} />
              <div>
                <h4 style={styles.contactInfoTitle}>Location</h4>
                <p style={styles.contactInfoText}>Karachi, Pakistan</p>
              </div>
            </div>

            <div style={styles.contactInfoItem}>
              <Mail size={24} style={{ color: '#ec4899' }} />
              <div>
                <h4 style={styles.contactInfoTitle}>Email</h4>
                <p style={styles.contactInfoText}>contact@codeai.pk</p>
              </div>
            </div>

            <div style={styles.contactInfoItem}>
              <Phone size={24} style={{ color: '#10b981' }} />
              <div>
                <h4 style={styles.contactInfoTitle}>Phone</h4>
                <p style={styles.contactInfoText}>+92 300 1234567</p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} style={styles.contactForm}>
            <input
              type="text"
              placeholder="Your Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              style={styles.contactInput}
              required
            />
            <input
              type="email"
              placeholder="Your Email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              style={styles.contactInput}
              required
            />
            <textarea
              placeholder="Your Message"
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              style={styles.contactTextarea}
              rows={6}
              required
            />
            <button type="submit" style={styles.contactButton}>
              Send Message
            </button>
          </form>
        </div>
      </div>
    </AnimatedSection>
  );
};


// ============================================
// MAIN PAGES
// ============================================
const MainPage = ({ user }) => {
  return (
    <>
      <HomeSection />
      <AboutSection />
      <BlogSection />
      <ContactSection />
    </>
  );
};

// ============================================
// APP LAYOUT WRAPPER (NEW!)
// ============================================
const AppLayout = ({ user, onLogout, children }) => {
  const location = useLocation();
  
  // Check if we're on the dashboard route
  const isDashboardRoute = location.pathname.startsWith('/dashboard');

  return (
    <>
      <div style={styles.gridBackground} />
      
      {/* Only show App navbar on non-dashboard routes */}
      {!isDashboardRoute && (
        <Navbar isAuthenticated={!!user} onLogout={onLogout} />
      )}
      
      <div style={styles.app}>
        {children}
      </div>
    </>
  );
};

// ============================================
// MAIN APP COMPONENT
// ============================================
const App = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    fetch('http://localhost:5000/api/check-session', {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        if (data.authenticated) {
          setUser(data.user);
        }
      })
      .catch(err => console.error('Session check failed:', err));
  }, []);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <Router>
      <AppLayout user={user} onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<MainPage user={user} />} />
          <Route path="/auth" element={<AuthPage onAuthSuccess={handleAuthSuccess} />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </AppLayout>
    </Router>
  );
};

// ============================================
// COMPLETE STYLES
// ============================================
const styles = {
  app: { 
    minHeight: '100vh', 
    width: '100%',
    backgroundColor: '#0a0a0f', 
    color: '#fff', 
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    position: 'relative',
  },

  gridBackground: { 
    position: 'fixed', 
    top: 0, 
    left: 0, 
    right: 0, 
    bottom: 0, 
    backgroundImage: 'linear-gradient(rgba(139, 92, 246, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(139, 92, 246, 0.03) 1px, transparent 1px)', 
    backgroundSize: '50px 50px', 
    pointerEvents: 'none', 
    zIndex: 0 
  },
  
  section: {
    minHeight: '100vh',
    position: 'relative',
    paddingTop: '90px',
    width: '100%',
  },

  scrollProgressContainer: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '3px',
    backgroundColor: 'transparent',
    zIndex: 10000,
    pointerEvents: 'none',
  },
  scrollProgressBar: {
    height: '100%',
    background: 'linear-gradient(90deg, #8b5cf6 0%, #ec4899 50%, #10b981 100%)',
    boxShadow: '0 0 10px rgba(139, 92, 246, 0.5)',
    transition: 'width 0.1s ease-out',
  },
  
  brandIcon: { 
    color: '#8b5cf6', 
    marginRight: '12px' 
  },
  brandText: { 
    fontSize: '20px', 
    fontWeight: '700', 
    background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)', 
    WebkitBackgroundClip: 'text', 
    WebkitTextFillColor: 'transparent' 
  },
  navLink: { 
    color: '#a1a1aa', 
    cursor: 'pointer', 
    fontSize: '15px', 
    transition: 'color 0.3s',
  },
  tryDemoBtn: { 
    padding: '10px 24px', 
    background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)', 
    border: 'none', 
    borderRadius: '8px', 
    color: '#fff', 
    fontWeight: '600', 
    cursor: 'pointer', 
    fontSize: '14px',
    transition: 'transform 0.3s',
  },
  logoutBtn: { 
    padding: '10px 24px', 
    background: 'rgba(239, 68, 68, 0.1)', 
    border: '1px solid rgba(239, 68, 68, 0.3)', 
    borderRadius: '8px', 
    color: '#ef4444', 
    fontWeight: '600', 
    cursor: 'pointer', 
    fontSize: '14px' 
  },
  mobileMenuBtn: { 
    display: 'none', 
    background: 'none', 
    border: 'none', 
    color: '#fff', 
    cursor: 'pointer', 
    padding: '8px' 
  },
// ============================================
// STYLES CONTINUATION (Add to App.jsx)
// ============================================

  mobileMenu: { 
    display: 'block', 
    backgroundColor: 'rgba(10, 10, 15, 0.95)',
    padding: '20px 0',
    position: 'absolute',
    top: '100%',
    pointerEvents: 'auto',
  },
  mobileLink: { 
    display: 'block', 
    padding: '16px 40px', 
    color: '#a1a1aa', 
    cursor: 'pointer', 
    borderBottom: '1px solid rgba(139, 92, 246, 0.1)' 
  },
  mobileTryDemoBtn: { 
    margin: '20px 40px', 
    padding: '14px 24px', 
    background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)', 
    border: 'none', 
    borderRadius: '8px', 
    color: '#fff', 
    fontWeight: '600', 
    cursor: 'pointer', 
    width: 'calc(100% - 80px)' 
  },

  // HOME SECTION
  heroSection: { 
    position: 'relative', 
    maxWidth: '1200px', 
    margin: '0 auto', 
    padding: '80px 40px', 
    textAlign: 'center',
    zIndex: 1,
  },
  glowOrb: { 
    position: 'absolute', 
    top: '100px', 
    left: '50%', 
    width: '600px', 
    height: '600px', 
    background: 'radial-gradient(circle, rgba(139, 92, 246, 0.25) 0%, rgba(236, 72, 153, 0.15) 40%, transparent 70%)', 
    pointerEvents: 'none', 
    filter: 'blur(80px)',
    transition: 'transform 0.1s ease-out',
  },
  heroTitle: { 
    fontSize: '64px', 
    fontWeight: '800', 
    lineHeight: '1.1', 
    marginBottom: '24px', 
    position: 'relative',
    transition: 'transform 0.1s ease-out',
    textShadow: '0 0 40px rgba(139, 92, 246, 0.3)',
    color: '#ffffff',
  },
  heroGradient: { 
    background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)', 
    WebkitBackgroundClip: 'text', 
    WebkitTextFillColor: 'transparent' 
  },
  heroSubtitle: { 
    fontSize: '20px', 
    color: '#c4c4cc', 
    maxWidth: '600px', 
    margin: '0 auto 40px',
    transition: 'transform 0.1s ease-out',
    textShadow: '0 0 20px rgba(0, 0, 0, 0.5)',
  },
  heroButton: { 
    padding: '16px 40px', 
    background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)', 
    border: 'none', 
    borderRadius: '12px', 
    color: '#fff', 
    fontSize: '18px', 
    fontWeight: '600', 
    cursor: 'pointer', 
    display: 'inline-flex', 
    alignItems: 'center', 
    boxShadow: '0 10px 40px rgba(139, 92, 246, 0.5), 0 0 60px rgba(236, 72, 153, 0.3)',
    transition: 'all 0.3s ease',
  },

  // FEATURE CARDS
  featureGrid: { 
    display: 'grid', 
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
    gap: '32px', 
    marginTop: '100px' 
  },
  featureCard: { 
    padding: '40px', 
    background: 'rgba(139, 92, 246, 0.08)', 
    border: '1px solid rgba(139, 92, 246, 0.3)', 
    borderRadius: '16px',
    cursor: 'pointer',
    boxShadow: '0 8px 32px rgba(139, 92, 246, 0.1)',
  },
  featureIcon: { 
    color: '#8b5cf6', 
    marginBottom: '20px' 
  },
  featureTitle: { 
    fontSize: '24px', 
    fontWeight: '700', 
    marginBottom: '12px' 
  },
  featureDescription: { 
    color: '#a1a1aa', 
    fontSize: '16px', 
    lineHeight: '1.6' 
  },

  // ABOUT SECTION
  aboutSection: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '80px 40px',
  },
  aboutContent: {
    position: 'relative',
    zIndex: 1,
  },
  aboutHeader: {
    textAlign: 'center',
    marginBottom: '80px',
  },
  sectionTitle: {
    fontSize: '48px',
    fontWeight: '800',
    marginBottom: '16px',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  sectionSubtitle: {
    fontSize: '18px',
    color: '#a1a1aa',
    maxWidth: '600px',
    margin: '0 auto',
  },
  aboutGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '32px',
    marginBottom: '80px',
  },
  aboutCard: {
    padding: '40px',
    background: 'rgba(17, 17, 27, 0.6)',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    borderRadius: '16px',
  },
  aboutCardTitle: {
    fontSize: '24px',
    fontWeight: '700',
    marginBottom: '12px',
  },
  aboutCardText: {
    color: '#a1a1aa',
    fontSize: '16px',
    lineHeight: '1.6',
  },
  statsSection: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '32px',
    padding: '60px 0',
    textAlign: 'center',
  },
  statItem: {
    padding: '20px',
  },
  statNumber: {
    fontSize: '48px',
    fontWeight: '800',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '8px',
  },
  statLabel: {
    fontSize: '16px',
    color: '#a1a1aa',
  },

  // BLOG SECTION
  blogSection: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '80px 40px',
  },
  blogHeader: {
    textAlign: 'center',
    marginBottom: '80px',
  },
  blogGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
    gap: '32px',
  },
  blogCard: {
    padding: '32px',
    background: 'rgba(17, 17, 27, 0.6)',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    borderRadius: '16px',
    cursor: 'pointer',
  },
  blogCardIcon: {
    color: '#8b5cf6',
    marginBottom: '16px',
  },
  blogCardDate: {
    fontSize: '14px',
    color: '#a1a1aa',
    marginBottom: '12px',
  },
  blogCardTitle: {
    fontSize: '22px',
    fontWeight: '700',
    marginBottom: '12px',
  },
  blogCardExcerpt: {
    color: '#a1a1aa',
    fontSize: '15px',
    lineHeight: '1.6',
    marginBottom: '20px',
  },
  blogCardButton: {
    padding: '10px 20px',
    background: 'rgba(139, 92, 246, 0.1)',
    border: '1px solid rgba(139, 92, 246, 0.3)',
    borderRadius: '8px',
    color: '#8b5cf6',
    fontWeight: '600',
    cursor: 'pointer',
    fontSize: '14px',
  },

  // CONTACT SECTION
  contactSection: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '80px 40px',
  },
  contactHeader: {
    textAlign: 'center',
    marginBottom: '80px',
  },
  contactContent: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '60px',
  },
  contactInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
  },
  contactInfoItem: {
    display: 'flex',
    gap: '20px',
    alignItems: 'flex-start',
  },
  contactInfoTitle: {
    fontSize: '18px',
    fontWeight: '700',
    marginBottom: '8px',
  },
  contactInfoText: {
    color: '#a1a1aa',
    fontSize: '16px',
  },
  contactForm: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  contactInput: {
    padding: '16px 20px',
    background: 'rgba(139, 92, 246, 0.05)',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    borderRadius: '10px',
    color: '#fff',
    fontSize: '16px',
    outline: 'none',
  },
  contactTextarea: {
    padding: '16px 20px',
    background: 'rgba(139, 92, 246, 0.05)',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    borderRadius: '10px',
    color: '#fff',
    fontSize: '16px',
    outline: 'none',
    fontFamily: 'inherit',
    resize: 'vertical',
  },
  contactButton: {
    padding: '16px',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)',
    border: 'none',
    borderRadius: '10px',
    color: '#fff',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
  },

};

export default App;