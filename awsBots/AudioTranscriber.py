import boto3
import botocore
import json
from urllib.parse import urlparse

class AudioTranscriber:
    def __init__(self, bucket_name, region='us-west-2'):
        self.bucket_name = bucket_name
        self.region      = region
        self.s3          = boto3.client('s3')
        self.transcribe  = boto3.client('transcribe', region_name=region)

    def upload_audio(self, local_file_path, s3_key):
        self.audio_file = local_file_path
        self.s3_key = s3_key
        self.s3.upload_file(local_file_path, self.bucket_name, s3_key)
        print(f"Uploaded {local_file_path} to s3://{self.bucket_name}/{s3_key}")

    def start_transcription(self, job_name, media_format='m4a', language_code='zh-TW'):
        self.job_name = job_name
        self.transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{self.bucket_name}/{self.s3_key}'},
            MediaFormat=media_format,
            LanguageCode=language_code,
            OutputBucketName=self.bucket_name  # ⬅️ 加這個！
        )

        print(f"Started transcription job: {job_name}")
    
    def safe_start_transcription(self, job_name, media_format='m4a', language_code='zh-TW'):
        try:
            self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            print(f"⚠️ Job '{job_name}' already exists, deleting it first...")
            self.transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] in ['NotFoundException', 'BadRequestException']:
                print(f"✅ No existing job named '{job_name}', ready to start.")
            else:
                raise e  # 其他錯誤才拋出
        # 開新 job
        self.start_transcription(job_name=job_name, media_format=media_format, language_code=language_code)

    def wait_for_completion(self):
        print("Waiting for transcription to complete...")
        while True:
            status = self.transcribe.get_transcription_job(TranscriptionJobName=self.job_name)
            state = status['TranscriptionJob']['TranscriptionJobStatus']
            if state in ['COMPLETED', 'FAILED']:
                break

        self.transcript_file_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        # print(f"Transcription {state}: {self.transcript_file_uri}")
        return state

    def get_transcribed_text(self):
        status = self.transcribe.get_transcription_job(TranscriptionJobName=self.job_name)
        transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        print('Transcript file URI:', transcript_uri)

        parsed_url = urlparse(transcript_uri)
        path_parts = parsed_url.path.lstrip('/').split('/')
        bucket = path_parts[0]
        key = '/'.join(path_parts[1:])

        print(f"Parsed bucket: {bucket}, key: {key}")

        s3 = boto3.client('s3')
        local_file = 'transcription_result.json'
        s3.download_file(bucket, key, local_file)

        with open(local_file, 'r', encoding='utf-8') as f:
            result_json = json.load(f)
        text = result_json['results']['transcripts'][0]['transcript']
        return text

    def delete_transcription_job(self):
        self.transcribe.delete_transcription_job(TranscriptionJobName=self.job_name)
        print(f"Deleted transcription job: {self.job_name}")

