try:
    from generated_openai_sdk import HelloWorldClient # type: ignore

    client = HelloWorldClient(base_url="http://localhost:8000")

    print("Testing root endpoint...")
    print(client.health_check())

except ImportError as e:
    print(f"Import error: {e}")
    print("\nTo generate the SDK, run:")
    print("1. Start the example server: python src/example_server.py")
    print(
        "2. Generate the SDK: sh standalone_generator.sh http://localhost:8000/openapi.json"
    )
    print("3. Then run this test again")
