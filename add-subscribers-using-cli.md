# Add subscribers using CLI

Using the CLI to add subscribers and slices is particularly efficient when dealing with multiple slices (e.g., 10 or more). This method enables batch additions and can be adjusted via the configuration options described below.

## Configuration File (mongo-tools/generate-data.py)
The default configuration (mongo-tools/generate-data.py) is shown below:

```python
DEFAULT_CONFIG = {
    "NUM_SLICES": 2,  # Number of network slices to create
    "NUM_COTS_SUBSCRIBERS": 0,  # Number of COTS subscribers
    "NUM_SAMPLE_SUBSCRIBERS": 2,  # Number of simulated subscribers
    "NUM_AUTO_GENERATED_SUBSCRIBERS": 0,  # Number of auto-generated subscribers (for MSD deployment only)
}
```

### Types of Subscribers

Our setup supports three types of subscribers:

- **NUM_COTS_SUBSCRIBERS**: Refers to Commercial Off-The-Shelf UEs configured with programmable SIM cards, used with USRP-based gNBs. Currently, these are configured for the UWaterloo lab.
- **NUM_SAMPLE_SUBSCRIBERS**: Denotes simulated UEs, such as subscriber_1, subscriber_2, and subscriber_3, for testing with UERANSIM. By default:
  - subscriber_1 and subscriber_3 connect to slice 1.
  - subscriber_2 connects to slice 2.
- **NUM_AUTO_GENERATED_SUBSCRIBERS**: Specifies the number of automatically generated simulated UEs. Each UE is assigned to slices in a round-robin fashion: For instance, if NUM_SUBSCRIBERS is 3 and NUM_SLICES is 2, the subscribers will be added as follows:
  - Slice 1: subscriber_101
  - Slice 2: subscriber_201
  - Slice 1: subscriber_102

    This automated addition is beneficial for scalability testing in multi-slice deployments.

> [!CAUTION] 
> The default Open5GS configuration in the project root supports up to **2 slices**. For additional slices, refer to the multi-slice deployment (msd) sub-directory.

## Adding subscribers
Ensure your virtual environment is active as described in as described in [Set up a virtual environment](README.md#1-set-up-a-virtual-environment).

1. Run the generate-data.py script, generates two files: `data/slices.yaml` and `data/subscribers.yaml`.

    ```bash
    (venv) dev@workshop-vm:~/open5gs-k8s$ python mongo-tools/generate-data.py 
    ```
    You should see output similar to the one below.
    ```bash
    2024-11-06 16:36:02 |     INFO | Loading existing data...
    2024-11-06 16:36:02 |     INFO | Creating 2 slices ...
    2024-11-06 16:36:02 |     INFO | Generating 0 new slices...
    2024-11-06 16:36:02 |     INFO | Saving slices to data/slices.yaml
    2024-11-06 16:36:02 |     INFO | Adding 2 sample subscribers ...
    2024-11-06 16:36:02 |     INFO | Saving subscribers to data/subscribers.yaml
    2024-11-06 16:36:02 |     INFO | Slice and subscriber creation complete.
    ```
2. Run add-subscribers.py to add the generated subscribers.

    ```bash
    (venv) dev@workshop-vm:~/open5gs-k8s$ python mongo-tools/add-subscribers.py 
    ```
    Expected output:

    ```bash
    2024-10-31 11:54:22 |     INFO | Added subscriber_1
    2024-10-31 11:54:22 |     INFO | Added subscriber_2
    ```

> [!NOTE]
> The default configuration will add 2 sample subscribers. To add a third sample subsciber, edit the configuration variable `NUM_SAMPLE_SUBSCRIBERS` to 3, then re-run `generate.py` and `add-subscribers.py`

3. You can verify if the subscribers were added with
   ```bash
   (venv) dev@workshop-vm:~/open5gs-k8s$ python mongo-tools/list-subscribers.py 
   ```
   You should see output similar to the one below.
   ```
   2024-10-31 11:55:36 |     INFO | subscriber_1
   2024-10-31 11:55:36 |     INFO | subscriber_2
   ```
4.	To delete all subscribers, use delete-subscribers.py.
```bash
(venv) dev@workshop-vm:~/open5gs-k8s$ python mongo-tools/delete-subscribers.py 
```
Example output:
```bash
2024-10-31 11:56:55 |     INFO | Deleted 001010000000001
2024-10-31 11:56:55 |     INFO | Deleted 001010000000002
```