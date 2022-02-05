norm_cfg = dict(type='BN', requires_grad=True)
backbone_norm_cfg = dict(type='LN', requires_grad=True)
model = dict(
    type='CustomEncoderDecoder',
    backbone=dict(
        type='SwinTransformer',
        pretrain_img_size=224,
        embed_dims=96,
        patch_size=4,
        window_size=7,
        mlp_ratio=4,
        depths=[2, 2, 6, 2],
        num_heads=[3, 6, 12, 24],
        strides=(4, 2, 2, 2),
        out_indices=(0, 1, 2, 3),
        qkv_bias=True,
        qk_scale=None,
        patch_norm=True,
        drop_rate=0.0,
        attn_drop_rate=0.0,
        drop_path_rate=0.3,
        use_abs_pos_embed=False,
        act_cfg=dict(type='GELU'),
        norm_cfg=backbone_norm_cfg
    ),
    decode_head=dict(
        type='UPerHead',
        in_channels=[96, 192, 384, 768],
        in_index=[0, 1, 2, 3],
        pool_scales=(1, 2, 3, 6),
        channels=512,
        dropout_ratio=0.1,
        num_classes=2,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0
        )
    ),
    auxiliary_head=dict(
        type='FCNHead',
        in_channels=384,
        in_index=2,
        channels=256,
        num_convs=1,
        concat_input=False,
        dropout_ratio=0.1,
        num_classes=2,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=0.4
        )
    ),
    train_cfg=dict(),
    test_cfg=dict(mode='whole')
)

dataset_type = 'GTBBoxDataset'
data_root = 'data/LIVECell_dataset_2021/'
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True
)

input_size = (128, 128)
train_pipeline = [
    dict(type='BoxJitter', prob=0.5),
    dict(type='ROIAlign', output_size=input_size),
    # dict(type='FlipRotate'),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg'])
]
test_pipeline = [
    dict(
        type='MultiScaleFlipAug',
        img_scale=input_size,
        flip=False,
        transforms=[
            dict(type='ROIAlign', output_size=input_size),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='BBoxFormat'),
            dict(type='Collect', keys=['img', 'bbox'])
        ]
    )
]
helper_dataset = dict(
    type='CellDataset',
    classes=(
        'shsy5y', 'a172', 'bt474', 'bv2', 'huh7', 'mcf7', 'skov3', 'skbr3'
    ),
    ann_file=data_root + 'val_8class.json',
    img_prefix=data_root + 'images/livecell_train_val_images',
    pipeline=[],
)
data = dict(
    samples_per_gpu=64,
    workers_per_gpu=2,
    train=dict(
        type='GTBBoxDataset',
        img_dir=data_root + 'images/livecell_train_val_images',
        ann_file=data_root + 'train_8class.json',
        helper_dataset=helper_dataset,
        pipeline=train_pipeline
    ),
    val=dict(
        type='PredBBoxDataset',
        # score_thr=0.3,
#         pred_file='work_dirs/yolox_x_livecell/val_preds.pkl',
        pred_file = '/content/drive/MyDrive/kaggle/Sartorius/work_dirs_1st/yolox_x_livecell/val_preds.pkl',
        img_dir=data_root + 'images/livecell_train_val_images',
        ann_file=data_root + 'val_8class.json',
        helper_dataset=helper_dataset,
        pipeline=test_pipeline
    ),
    test=dict(
        type='PredBBoxDataset',
#         pred_file='work_dirs/yolox_x_livecell/val_preds.pkl',
        pred_file = '/content/drive/MyDrive/kaggle/Sartorius/work_dirs_1st/yolox_x_livecell/val_preds.pkl',
        img_dir=data_root + 'images/livecell_train_val_images',
        ann_file=data_root + 'val_8class.json',
        helper_dataset=helper_dataset,
        pipeline=test_pipeline
    )
)
log_config = dict(
    interval=50, hooks=[dict(type='TextLoggerHook', by_epoch=True)]
)
dist_params = dict(backend='nccl')
log_level = 'INFO'
load_from = 'https://download.openmmlab.com/mmsegmentation/v0.5/swin/upernet_swin_tiny_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K/upernet_swin_tiny_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K_20210531_112542-e380ad3e.pth'
work_dir = '/content/drive/MyDrive/kaggle/Sartorius/work_dirs_1st/upernet_swin-t_livecell/'
resume_from = None
workflow = [('train', 1)]
cudnn_benchmark = True
optimizer = dict(
    type='AdamW',
    lr=6e-05 / 16,
    betas=(0.9, 0.999),
    weight_decay=0.01,
    paramwise_cfg=dict(
        custom_keys=dict(
            absolute_pos_embed=dict(decay_mult=0.0),
            relative_position_bias_table=dict(decay_mult=0.0),
            norm=dict(decay_mult=0.0)
        )
    )
)
optimizer_config = dict()
lr_config = dict(
    policy='CosineAnnealing',
    by_epoch=False,
    warmup='linear',
    warmup_iters=100,
    warmup_ratio=1.0 / 10,
    min_lr_ratio=1e-5
)
runner = dict(type='EpochBasedRunner', max_epochs=1)
checkpoint_config = dict(interval=1, save_optimizer=False)
evaluation = dict(interval=1, metric='dummy', pre_eval=True)
