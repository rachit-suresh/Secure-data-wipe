Before: In your terminal, run dd if=/dev/urandom of=test_drive.img bs=1M count=100 to generate a file with 100mb of random data then use a command like hexdump -C test_drive.img | head to show that the file is full of random data.

Run: Start your Flask server: python app.py.

Trigger: Your frontend (or a tool like Postman) sends a POST request to http://127.0.0.1:5000/wipe with the JSON body: {"device_name": "test_drive.img"}.

Monitor: The frontend can then poll the GET http://127.0.0.1:5000/status/<log_id> endpoint every few seconds to show the status changing from pending -> wiping -> completed.

After: Run hexdump -C test_drive.img | head again. This time, it will show all zeros. This is your "proof" that the data has been erased.