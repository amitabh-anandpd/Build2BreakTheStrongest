from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained("Lightricks/LTX-Video", dtype=torch.float16)
pipe.save_pretrained("ltx_model")
