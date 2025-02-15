"""将 resnet50 -> rknn"""
from rknn.api import RKNN
import torch

IMG_SIZE = 640


def export_jit_pt(model_path, save_name):
    """模型导出为 jit pt"""
    model = torch.load(model_path, map_location='cpu')
    model.eval()
    trace_model = torch.jit.trace(model, torch.Tensor(1, 3, IMG_SIZE, IMG_SIZE))
    trace_model.save(f'./{save_name}_jit.pt')
    return


def export_rknn(model_path, save_name):
    # export_jit_pt(model_path, save_name)  # 先导出 pt 模型
    # model = f'./{save_name}_jit.pt'
    model = model_path
    input_size_list = [[3, IMG_SIZE, IMG_SIZE]]

    rknn = RKNN()
    # pre-process config
    print('--> Config model')
    rknn.config(mean_values=[[0, 0, 0]], std_values=[[255, 255, 255]],
                reorder_channel='0 1 2', target_platform='RK3399Pro')
    print('done')

    # Load Pytorch model
    print('--> Loading model')
    ret = rknn.load_pytorch(model=model, input_size_list=input_size_list)
    if ret != 0:
        print('Load Pytorch model failed!')
        exit(ret)
    print('done')

    # Build model
    print('--> Building model')
    ret = rknn.build(do_quantization=True, dataset='./dataset.txt')
    if ret != 0:
        print('Build model failed!')
        exit(ret)
    print('done')

    # Export RKNN model
    print('--> Export RKNN model')
    ret = rknn.export_rknn(f'./{save_name}.rknn')
    if ret != 0:
        print('Export resnet50.rknn failed!')
        exit(ret)
    print('done')
    return


def load_rknn_model(model_file):
    """通过 .rknn 文件加载模型"""
    from rknn.api import RKNN
    # 模型加载之前需要进行解密处理
    rknn = RKNN()
    ret = rknn.load_rknn(model_file)
    if ret != 0:
        print('load rknn model failed')
    ret = rknn.init_runtime()
    if ret != 0:
        print('Init runtime environment failed')
    return rknn


def run(model_file, img):
    model = load_rknn_model(model_file)
    outputs = model.inference(inputs=[img])
    return outputs


if __name__ == '__main__':
    export_rknn('yolov5s.onnx', 'yolov5s')
