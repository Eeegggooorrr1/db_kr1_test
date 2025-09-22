from db.models import AttackTypeEnum

experiments_data = [
    {
        "name": "Baseline Classification",
        "description": "Базовый эксперимент по классификации изображений без атак",
    },
    {
        "name": "Adversarial Robustness Test",
        "description": "Тестирование устойчивости к adversarial атакам",
    },
    {
        "name": "Noise Resistance Study",
        "description": "Исследование устойчивости к различным типам шума",
    }
]

runs_data = [
    {
        "experiment_id": 1,
        "accuracy": 0.95,
        "flagged": False
    },
    {
        "experiment_id": 1,
        "accuracy": 0.96,
        "flagged": False
    },

    {
        "experiment_id": 2,
        "accuracy": 0.45,
        "flagged": True
    },
    {
        "experiment_id": 2,
        "accuracy": 0.62,
        "flagged": False
    },

    {
        "experiment_id": 3,
        "accuracy": 0.78,
        "flagged": False
    },
    {
        "experiment_id": 3,
        "accuracy": 0.82,
        "flagged": False
    }
]

images_data = [
    {
        "run_id": 1,
        "file_path": "/data/run1/img_001.png",
        "original_name": "cat_001.png",
        "attack_type": AttackTypeEnum.no_attack,
        "coordinates": [100, 150, 200, 250]
    },
    {
        "run_id": 1,
        "file_path": "/data/run1/img_002.jpg",
        "original_name": "dog_001.jpg",
        "attack_type": AttackTypeEnum.no_attack,
        "coordinates": [50, 75, 180, 220]
    },

    {
        "run_id": 2,
        "file_path": "/data/run2/img_003.jpg",
        "original_name": "bird_001.jpg",
        "attack_type": AttackTypeEnum.no_attack,
        "coordinates": [120, 80, 250, 180]
    },

    {
        "run_id": 3,
        "file_path": "/data/run3/adv_001.jpeg",
        "original_name": "cat_002.jpeg",
        "attack_type": AttackTypeEnum.adversarial,
        "coordinates": [90, 130, 190, 240]
    },
    {
        "run_id": 3,
        "file_path": "/data/run3/adv_002.jpg",
        "original_name": "dog_002.jpg",
        "attack_type": AttackTypeEnum.adversarial,
        "coordinates": [60, 85, 170, 210]
    },

    {
        "run_id": 4,
        "file_path": "/data/run4/adv_003.png",
        "original_name": "car_001.png",
        "attack_type": AttackTypeEnum.adversarial,
        "coordinates": [30, 40, 220, 160]
    },

    {
        "run_id": 5,
        "file_path": "/data/run5/noise_001.jpg",
        "original_name": "street_001.jpg",
        "attack_type": AttackTypeEnum.noise,
        "coordinates": [10, 20, 300, 400]
    },
    {
        "run_id": 5,
        "file_path": "/data/run5/noise_002.png",
        "original_name": "building_001.jpg",
        "attack_type": AttackTypeEnum.blur,
        "coordinates": [5, 15, 280, 380]
    },

    {
        "run_id": 6,
        "file_path": "/data/run6/rot_001.jpg",
        "original_name": "person_001.jpg",
        "attack_type": AttackTypeEnum.other,
        "coordinates": [80, 120, 240, 320]
    },
    {
        "run_id": 6,
        "file_path": "/data/run6/mixed_001.jpeg",
        "original_name": "animal_001.jpeg",
        "attack_type": AttackTypeEnum.noise,
        "coordinates": [70, 90, 210, 290]
    }
]