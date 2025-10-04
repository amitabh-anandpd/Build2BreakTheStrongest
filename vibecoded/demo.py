"""
demo.py - Demonstration script showing various usage examples
"""

import os
from main import PDFtoShortsConverter, VideoConfig


def demo_basic():
    """Basic usage example"""
    print("=" * 60)
    print("DEMO 1: Basic PDF to Short Conversion")
    print("=" * 60)
    
    # Get API key from environment or input
    api_key = os.environ.get('GEMINI_API_KEY') or input("Enter your Gemini API key: ")
    
    # Create converter with default settings
    converter = PDFtoShortsConverter(gemini_api_key=api_key)
    
    # Process a PDF
    pdf_path = "example.pdf"  # Replace with your PDF
    output_path = converter.process_pdf(pdf_path)
    
    print(f"\n✅ Video created: {output_path}")


def demo_custom_config():
    """Example with custom configuration"""
    print("=" * 60)
    print("DEMO 2: Custom Configuration")
    print("=" * 60)
    
    api_key = os.environ.get('GEMINI_API_KEY') or input("Enter your Gemini API key: ")
    
    # Custom configuration
    config = VideoConfig(
        duration=45,           # 45-second video
        width=1080,
        height=1920,
        fps=30,
        style='whiteboard'     # Whiteboard style instead of doodle
    )
    
    converter = PDFtoShortsConverter(
        gemini_api_key=api_key,
        config=config
    )
    
    output_path = converter.process_pdf(
        pdf_path="example.pdf",
        output_path="custom_short.mp4"
    )
    
    print(f"\n✅ Custom video created: {output_path}")


def demo_batch_processing():
    """Process multiple PDFs"""
    print("=" * 60)
    print("DEMO 3: Batch Processing")
    print("=" * 60)
    
    api_key = os.environ.get('GEMINI_API_KEY') or input("Enter your Gemini API key: ")
    
    # List of PDFs to process
    pdf_files = [
        "document1.pdf",
        "document2.pdf",
        "document3.pdf"
    ]
    
    converter = PDFtoShortsConverter(gemini_api_key=api_key)
    
    results = []
    for i, pdf_path in enumerate(pdf_files, 1):
        if not os.path.exists(pdf_path):
            print(f"⚠️  Skipping {pdf_path} (not found)")
            continue
        
        print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_path}")
        
        output_name = f"short_{i:02d}.mp4"
        try:
            output_path = converter.process_pdf(pdf_path, output_name)
            results.append({'pdf': pdf_path, 'video': output_path, 'status': 'success'})
        except Exception as e:
            print(f"❌ Error processing {pdf_path}: {e}")
            results.append({'pdf': pdf_path, 'video': None, 'status': 'failed'})
    
    # Summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {result['pdf']} -> {result['video']}")


def demo_step_by_step():
    """Show step-by-step processing for educational purposes"""
    print("=" * 60)
    print("DEMO 4: Step-by-Step Processing")
    print("=" * 60)
    
    api_key = os.environ.get('GEMINI_API_KEY') or input("Enter your Gemini API key: ")
    
    pdf_path = "example.pdf"
    
    # Step 1: Extract content
    print("\n📄 Step 1: Extracting content from PDF...")
    from agents.content_extractor import ContentExtractor
    extractor = ContentExtractor()
    extracted_data = extractor.extract(pdf_path)
    print(f"   - Extracted {len(extracted_data['text'])} characters")
    print(f"   - Found {len(extracted_data['sections'])} sections")
    print(f"   - Title: {extracted_data['metadata']['title']}")
    
    # Step 2: Generate script
    print("\n✍️  Step 2: Generating script with Gemini...")
    from agents.script_writer import ScriptWriter
    script_writer = ScriptWriter(api_key)
    script = script_writer.generate_script(extracted_data, max_duration=60)
    print(f"   - Generated {len(script['scenes'])} scenes")
    print(f"   - Hook: {script.get('hook', 'N/A')[:80]}...")
    
    # Step 3: Create visuals
    print("\n🎨 Step 3: Creating visuals...")
    from agents.visuals_maker import VisualsMaker
    visuals_maker = VisualsMaker(style='doodle')
    visual_assets = visuals_maker.generate_visuals(script)
    print(f"   - Created {len(visual_assets)} visual assets")
    
    # Step 4: Generate narration
    print("\n🎙️  Step 4: Generating narration...")
    from agents.narrator import Narrator
    narrator = Narrator()
    audio_path = narrator.generate_audio(script)
    print(f"   - Audio saved to: {audio_path}")
    
    # Step 5: Compose video
    print("\n🎬 Step 5: Composing final video...")
    from agents.video_composer import VideoComposer
    config = VideoConfig()
    composer = VideoComposer(config)
    final_video = composer.compose(
        script=script,
        visual_assets=visual_assets,
        audio_path=audio_path,
        output_path="step_by_step_output.mp4",
        citations=extracted_data.get('citations', [])
    )
    
    print(f"\n✅ Complete! Video saved to: {final_video}")


def demo_test_components():
    """Test individual components"""
    print("=" * 60)
    print("DEMO 5: Component Testing")
    print("=" * 60)
    
    # Test 1: Content Extractor
    print("\n🧪 Test 1: Content Extractor")
    try:
        from agents.content_extractor import ContentExtractor
        extractor = ContentExtractor()
        # Create a dummy PDF for testing if none exists
        print("   ✅ ContentExtractor initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Script Writer (requires API key)
    print("\n🧪 Test 2: Script Writer")
    try:
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            from agents.script_writer import ScriptWriter
            script_writer = ScriptWriter(api_key)
            print("   ✅ ScriptWriter initialized with API key")
        else:
            print("   ⚠️  Skipped (no API key in environment)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Visuals Maker
    print("\n🧪 Test 3: Visuals Maker")
    try:
        from agents.visuals_maker import VisualsMaker
        visuals_maker = VisualsMaker()
        print("   ✅ VisualsMaker initialized")
        
        # Test generating a simple visual
        test_scene = {
            'scene_number': 1,
            'duration': 10,
            'narration': 'Test narration',
            'visual_description': 'A circle and an arrow',
            'visual_elements': ['circle', 'arrow'],
            'animation_type': 'draw_on'
        }
        visual_path = visuals_maker._generate_scene_visual(test_scene, 1)
        if os.path.exists(visual_path):
            print(f"   ✅ Test visual created: {visual_path}")
        else:
            print("   ⚠️  Visual file not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Narrator
    print("\n🧪 Test 4: Narrator")
    try:
        from agents.narrator import Narrator
        narrator = Narrator()
        print("   ✅ Narrator initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Video Composer
    print("\n🧪 Test 5: Video Composer")
    try:
        from agents.video_composer import VideoComposer
        config = VideoConfig()
        composer = VideoComposer(config)
        print("   ✅ VideoComposer initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Component testing complete!")


def demo_different_styles():
    """Compare different visual styles"""
    print("=" * 60)
    print("DEMO 6: Visual Style Comparison")
    print("=" * 60)
    
    api_key = os.environ.get('GEMINI_API_KEY') or input("Enter your Gemini API key: ")
    
    pdf_path = "example.pdf"
    styles = ['doodle', 'whiteboard', 'sketch']
    
    for style in styles:
        print(f"\n🎨 Creating {style} style video...")
        
        config = VideoConfig(
            duration=30,  # Shorter for comparison
            style=style
        )
        
        converter = PDFtoShortsConverter(
            gemini_api_key=api_key,
            config=config
        )
        
        output_path = f"output_{style}.mp4"
        
        try:
            converter.process_pdf(pdf_path, output_path)
            print(f"   ✅ {style} video created: {output_path}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Style comparison complete! Compare the output files.")


def main():
    """Main demo menu"""
    print("\n" + "=" * 60)
    print("PDF to YouTube Shorts - Demo Suite")
    print("=" * 60)
    
    demos = {
        '1': ('Basic Usage', demo_basic),
        '2': ('Custom Configuration', demo_custom_config),
        '3': ('Batch Processing', demo_batch_processing),
        '4': ('Step-by-Step Processing', demo_step_by_step),
        '5': ('Component Testing', demo_test_components),
        '6': ('Visual Style Comparison', demo_different_styles),
    }
    
    print("\nAvailable Demos:")
    for key, (name, _) in demos.items():
        print(f"  {key}. {name}")
    print("  0. Run all demos")
    print("  q. Quit")
    
    choice = input("\nSelect demo to run: ").strip()
    
    if choice == 'q':
        print("Goodbye!")
        return
    
    if choice == '0':
        print("\n🚀 Running all demos...")
        for name, demo_func in demos.values():
            print(f"\n{'='*60}")
            print(f"Running: {name}")
            print('='*60)
            try:
                demo_func()
            except Exception as e:
                print(f"❌ Demo failed: {e}")
            input("\nPress Enter to continue to next demo...")
    elif choice in demos:
        name, demo_func = demos[choice]
        print(f"\n🚀 Running: {name}")
        try:
            demo_func()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    # Check for required environment variables
    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠️  Tip: Set GEMINI_API_KEY environment variable to skip entering it each time")
        print("   Example: export GEMINI_API_KEY='your-api-key'\n")
    
    main()