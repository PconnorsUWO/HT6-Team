# Virtual Try-On App 🎽

A revolutionary clothing try-on application that allows users to virtually try on garments using AI-powered image transformation. Built for hackathon innovation with real-time video recording, intelligent frame selection, and AI-powered clothing recommendations.

## 🚀 Features

### Core Functionality

- **Real-time Video Recording**: Capture video directly from your device camera
- **Intelligent Frame Selection**: AI-powered analysis to find the best frames for try-on
- **Virtual Try-On**: Upload or select preset garments and instantly see yourself wearing them
- **AI-Powered Image Transformation**: Advanced computer vision to seamlessly blend garments onto your body
- **Multiple Input Methods**: Support for both custom uploads and preset garment selection

### Smart Video Processing

- **TwelveLabs Integration**: Semantic video search to find optimal frames
- **Automatic Frame Selection**: AI identifies frames where user is standing still with good lighting
- **Real-time Processing**: Fast video analysis and frame extraction

### Recommendation System

- **Intelligent Clothing Suggestions**: Powered by [Vellum AI](https://www.vellum.ai/) for personalized recommendations
- **Style Matching**: AI-driven outfit coordination based on user preferences and selected garments
- **Trend Analysis**: Real-time fashion trend integration

### Data Management

- **MongoDB Atlas Storage**: Secure cloud storage for user data, garments, and try-on results
- **User History**: Track and retrieve previous try-on sessions
- **Preset Garments**: Curated collection of popular clothing items

### Technical Features

- **RESTful API**: Scalable backend architecture
- **Real-time Processing**: Fast image transformation with progress tracking
- **Cross-platform Compatibility**: Works on desktop and mobile browsers
- **Secure File Handling**: Temporary storage with automatic cleanup

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Services   │
│   (React)       │◄──►│   (Flask API)   │◄──►│   (IDM-VTON)    │
│                 │    │                 │    │                 │
│ • Video Capture │    │ • Video Upload  │    │ • Virtual Try-On│
│ • Garment Select│    │ • Frame Analysis│    │ • Image Processing│
│ • Results Display│   │ • MongoDB       │    │ • AI Models     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   MongoDB Atlas │
                       │                 │
                       │ • User Data     │
                       │ • Garments      │
                       │ • Try-on Results│
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   TwelveLabs    │
                       │                 │
                       │ • Video Analysis│
                       │ • Frame Search  │
                       │ • Semantic Search│
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Vellum AI     │
                       │                 │
                       │ • Recommendations│
                       │ • Style Matching│
                       │ • Trend Analysis│
                       └─────────────────┘
```

## 📱 User Flow

1. **User Authentication**: User logs in (authentication to be implemented)
2. **Garment Selection**: User uploads a custom garment OR selects from preset garments (stored in MongoDB)
3. **Video Recording**: User starts video recording from their device camera
4. **AI Frame Analysis**: Video is sent to TwelveLabs for semantic video search to find the best frames where the user is standing still
5. **Frame Selection**: Optimal frame is sent back to frontend, and user is notified that their clothes are being replaced
6. **Virtual Try-On**: Our try-on endpoint runs the IDM-VTON model, processes the image, and uploads the result to MongoDB
7. **Result Display**: Public URL of the transformed image is fed back to the frontend
8. **AI Recommendations**: Vellum AI generates complementary clothing recommendations based on the selected garment

## 🛠️ Tech Stack

### Frontend

- **React** - Modern UI framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool
- **Webcam API** - Real-time camera integration

### Backend

- **Flask** - Python web framework
- **Gradio Client** - AI model integration
- **MongoDB Atlas** - Cloud database
- **Flask-CORS** - Cross-origin support
- **TwelveLabs API** - Video analysis and frame selection
- **Vellum AI** - Recommendation engine

### AI & ML

- **IDM-VTON** - Virtual try-on model
- **TwelveLabs** - Video understanding and frame analysis
- **Vellum AI** - Intelligent recommendation system
- **Computer Vision** - Image processing

### Infrastructure

- **MongoDB Atlas** - Cloud database
- **Hugging Face Spaces** - AI model hosting
- **RESTful APIs** - Service communication

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB Atlas account
- Vellum AI API access
- TwelveLabs API access
- Webcam-enabled device

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd HT6-Team
```

### 2. Backend Setup

```bash
cd backend
uv add flask flask-cors werkzeug gradio-client requests pymongo python-dotenv
uv run -- flask run -p 3000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Environment Configuration

Create `.env` files in both frontend and backend directories:

**Backend (.env)**

```env
MONGODB_URI=your_mongodb_atlas_connection_string
VELLUM_API_KEY=your_vellum_api_key
TWELVELABS_API_KEY=your_twelvelabs_api_key
FLASK_ENV=development
```

**Frontend (.env)**

```env
VITE_API_URL=http://localhost:3000
VITE_VELLUM_API_KEY=your_vellum_api_key
VITE_TWELVELABS_API_KEY=your_twelvelabs_api_key
```

## 📖 API Documentation

### Core Endpoints

#### Health Check

```http
GET /health
```

#### Preset Garments

```http
GET /preset-garments
```

#### Upload Custom Garment

```http
POST /upload-garment
Content-Type: multipart/form-data

garment_image: [file]
user_id: "user123"
description: "Blue casual shirt"
```

#### Process Video Recording

```http
POST /process-video
Content-Type: multipart/form-data

video_file: [file]
```

#### Virtual Try-On

```http
POST /tryon
Content-Type: application/x-www-form-urlencoded

person_image_path: "/path/to/frame.jpg"
garment_id: "blue_shirt"
user_id: "user123"
```

#### User History

```http
GET /user-history/{user_id}
```

## 🎯 Hackathon Tracks

### 🏆 Innovation Track

- **AI-Powered Video Analysis**: Real-time video processing with TwelveLabs
- **Intelligent Frame Selection**: Automatic detection of optimal try-on frames
- **Advanced Image Processing**: Seamless garment blending with IDM-VTON
- **Smart Recommendations**: AI-driven outfit suggestions with Vellum

### 🎨 User Experience Track

- **Intuitive Video Interface**: Simple video recording and processing
- **Real-time Feedback**: Instant visual results and recommendations
- **Mobile Responsive**: Works across all devices
- **Seamless Workflow**: From video to try-on to recommendations

### 🤖 AI/ML Track

- **Computer Vision**: Advanced image transformation algorithms
- **Video Understanding**: Semantic video search and frame analysis
- **Recommendation Engine**: Personalized clothing suggestions
- **Machine Learning**: Continuous improvement through user feedback

### ☁️ Cloud & Infrastructure Track

- **MongoDB Atlas**: Scalable cloud database for user data and results
- **Microservices**: Modular API architecture
- **Performance Optimization**: Fast response times for video processing
- **Data Management**: Efficient storage and retrieval of try-on results

### 🔒 Security & Privacy Track

- **Secure File Handling**: Temporary storage with cleanup
- **Data Privacy**: User data protection in MongoDB Atlas
- **API Security**: Rate limiting and validation
- **Video Privacy**: Secure video processing and storage

### 🌱 Sustainability Track (Deloitte Green AI)

- **Reduce Returns**: Virtual try-on reduces physical returns and shipping
- **Sustainable Fashion**: Promote eco-friendly clothing choices
- **Carbon Footprint Reduction**: Less physical shopping trips
- **Digital Fashion**: Reduce textile waste through virtual try-on

## 📱 User Flow Details

### Step 1: User Authentication

- User logs in (authentication system to be implemented)
- Session management and user identification

### Step 2: Garment Selection

- **Option A**: Upload custom garment image
  - File validation and processing
  - Storage in MongoDB with metadata
- **Option B**: Select from preset garments
  - Curated collection of popular items
  - Pre-processed and optimized images

### Step 3: Video Recording

- Real-time video capture from device camera
- Video quality optimization for processing
- Temporary local storage

### Step 4: AI Frame Analysis

- Video upload to TwelveLabs API
- Semantic search for optimal frames
- Criteria: person standing still, full body visible, good lighting
- Automatic frame selection and extraction

### Step 5: Frame Processing

- Selected frame sent to frontend
- User notification of processing status
- Frame optimization for try-on model

### Step 6: Virtual Try-On

- IDM-VTON model processing
- Garment overlay and blending
- Result generation and optimization

### Step 7: Result Storage

- Transformed image uploaded to MongoDB
- Public URL generation for sharing
- Metadata storage (user, garment, timestamp)

### Step 8: AI Recommendations

- Vellum AI analysis of selected garment
- Context-aware recommendations
- Style matching and coordination suggestions

## 🔧 Development

### Project Structure

```
HT6-Team/
├── backend/
│   ├── app.py              # Flask API server with new endpoints
│   ├── test_api.py         # API testing
│   ├── pyproject.toml      # Python dependencies
│   ├── uploads/            # Temporary file storage
│   └── README.md          # Backend documentation
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node dependencies
│   └── README.md          # Frontend documentation
└── README.md              # Main project documentation
```

### Key Components

#### Backend Services

- **Video Processing**: Handle video uploads and TwelveLabs integration
- **Frame Analysis**: AI-powered frame selection and optimization
- **Garment Management**: Upload, storage, and retrieval of garments
- **Try-On Processing**: IDM-VTON model integration
- **Recommendation Engine**: Vellum AI integration for suggestions
- **Database Operations**: MongoDB Atlas CRUD operations

#### Frontend Components

- **Video Capture**: Real-time camera integration
- **Garment Selection**: Upload and preset garment interface
- **Frame Display**: Show selected optimal frames
- **Result Visualization**: Image transformation display
- **Recommendation UI**: AI-powered suggestions display

## 🧪 Testing

### Backend Testing

```bash
cd backend
uv run python test_api.py
```

### API Testing

```bash
# Health check
curl http://localhost:3000/health

# Get preset garments
curl http://localhost:3000/preset-garments

# Upload custom garment
curl -X POST http://localhost:3000/upload-garment \
  -F "garment_image=@garment.jpg" \
  -F "user_id=user123" \
  -F "description=Blue shirt"

# Process video
curl -X POST http://localhost:3000/process-video \
  -F "video_file=@recording.mp4"

# Virtual try-on
curl -X POST http://localhost:3000/tryon \
  -d "person_image_path=/path/to/frame.jpg" \
  -d "garment_id=blue_shirt" \
  -d "user_id=user123"
```

## 🚀 Deployment

### Backend Deployment

```bash
# Production setup
export FLASK_ENV=production
export MONGODB_URI=your_production_mongodb_uri
export VELLUM_API_KEY=your_production_vellum_key
export TWELVELABS_API_KEY=your_production_twelvelabs_key
uv run python app.py
```

### Frontend Deployment

```bash
cd frontend
npm run build
# Deploy dist/ folder to your hosting service
```

## 📊 Performance Metrics

- **Video Processing**: < 30 seconds for frame analysis
- **Image Processing**: < 30 seconds per transformation
- **API Response**: < 2 seconds for health checks
- **File Upload**: Support for up to 16MB files
- **Concurrent Users**: Scalable architecture for multiple users

## 🔮 Future Enhancements

### Phase 2 Features

- **AR Integration**: Augmented reality try-on
- **Social Sharing**: Share results on social media
- **E-commerce Integration**: Direct purchase from recommendations
- **Advanced Analytics**: User behavior tracking

### Phase 3 Features

- **3D Modeling**: Three-dimensional garment visualization
- **Voice Commands**: Hands-free operation
- **Multi-language Support**: International user base
- **Advanced AI**: More sophisticated recommendation algorithms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **IDM-VTON Team**: Virtual try-on model
- **[Vellum AI](https://www.vellum.ai/)**: Recommendation engine
- **[TwelveLabs](https://twelvelabs.io/)**: Video understanding platform
- **MongoDB Atlas**: Cloud database infrastructure
- **Hugging Face**: AI model hosting platform

## 📞 Support

For support, email support@virtualtryon.com or join our Slack channel.

---

**Built with ❤️ for the hackathon community**
