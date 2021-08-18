# :newspaper: 뉴스 토픽 분류 AI 경진대회

### 주제 : 한국어 뉴스 헤드라인을 이용하여, 뉴스의 주제를 분류하는 알고리즘 개발

주최 : Dacon

기간 : 2021년 6월 30일 ~ 2021년 8월 9일

평가 : Accuracy

팀원 : 김진현, 허윤성 (Daon)

링크 : https://dacon.io/competitions/official/235747/overview/description



## :trophy: Result


Public LB : 0.87031 (14등)

Private LB : 0.83223 (16등)

Code Sharing : [Link][https://dacon.io/competitions/official/235747/codeshare/3071?page=1&dtype=recent]



## :black_large_square: Installation




```shell
# install necessary tools
pip install -r requirements.txt
```



## :desktop_computer: Command Line

**Training**

```shell
python3 main.py --wandb_project_name [project_name] --wandb_run_name [initial_name_comment] --model_name [model_name] --huggingface_model [pretrained_model_name]
# ex) python main.py --wandb_project name news_data --wandb_run_name JH_bert_kykim --model_name Bert -- huggingface_model kykim/bert-base-kor
```

**Test**

```shell
python3 inference.py --wandb_project_name [project_name] --wandb_run_name [initial_name_comment] --model_name [model_name] --huggingface_model [pretrained_model_name] --best_epoch [list]
# ex) python inference.py --wandb_project name --wandb_run_name JH_bert_kykim --model_name Bert -- huggingface_model kykim/bert-base-kor --best_epoch 1,2,3,4,5
```

**Arguments**

`wandb_project` : wandb 사용을 위한 프로젝트 이름 작성

`wandb_run_name` : wandb 사용을 위한 프로젝트 내 모델 결과 확인 이름 작성

`model_name` : 사용 모델 이름 작성(XLM, Electra, Bert)

`huggingface_model` : Huggingface의 Pretrained model 이름 작성

- Bert : `klue/bert-base`, `kykim/bert-kor-base`
- Electra : `monologg/koelectra-base-v3-discriminator`
- XLM : `klue/roberta-base` `klue/roberta-large`

`best_epoch` : Fold별 가장 높은 모델 불러오기 위한 list



## :diamond_shape_with_a_dot_inside: Directory structure


```bash
├── README.md                 
├── requirements.txt          - 필요한 library
[pyfile]
├── args.py                   
├── eda_data.py               - Data EDA를 위한 코드
├── func.py                   - Focal Loss / Custom Scheduler 코드
├── inference.py
├── load_data.py              - DataLoader 제작
├── main.py
├── model.py                  - Tokenizer / model 분류
├── optimizer_scheduler.py
├── util.py                   - Seed / Loss_function / Accuracy
[notebook]
├── notebook/                 - Data Augmentation을 위한 notebook
    └── gpt.ipynb
    └── pororo.ipynb
```

