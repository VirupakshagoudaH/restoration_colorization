

import os
import argparse
import shutil
import sys
from subprocess import call

def run_cmd(command):
    try:
        call(command, shell=True)
    except KeyboardInterrupt:
        print("Process interrupted")
        sys.exit(1)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", type=str, default="/content/photo_restoration/test_images/upload", help="Test images")
    parser.add_argument(
        "--output_folder",
        type=str,
        default="/content/photo_restoration/upload_output",
        help="Restored images, please use the absolute path",
    )
    parser.add_argument("--GPU", type=str, default="0", help="0,1,2")
    parser.add_argument(
        "--checkpoint_name", type=str, default="Setting_9_epoch_100", help="choose which checkpoint"
    )
    parser.add_argument("--with_scratch",default="1",action="store_true")
    opts = parser.parse_args()

    gpu1 = opts.GPU

    
    opts.input_folder = os.path.abspath(opts.input_folder)
    opts.output_folder = os.path.abspath(opts.output_folder)
    if not os.path.exists(opts.output_folder):
        os.makedirs(opts.output_folder)

    main_environment = os.getcwd()

    
    print("Running Overall Restoration")
    os.chdir("./scratch_removal")
    stage_1_input_dir = opts.input_folder
    stage_1_output_dir = os.path.join(opts.output_folder, "stage_1_restore_output")
    if not os.path.exists(stage_1_output_dir):
        os.makedirs(stage_1_output_dir)

    if not opts.with_scratch:
        scratch_remove_cmd = (
            "python test.py --test_mode Full --Quality_restore --test_input "
            + stage_1_input_dir
            + " --outputs_dir "
            + stage_1_output_dir
            + " --gpu_ids "
            + gpu1
        )
        run_cmd(scratch_remove_cmd)
    else:

        mask_dir = os.path.join(stage_1_output_dir, "masks")
        new_input = os.path.join(mask_dir, "input")
        new_mask = os.path.join(mask_dir, "mask")
        scratch_remove_cmd_1 = (
            "python scratch_detection.py --test_path "
            + stage_1_input_dir
            + " --output_dir "
            + mask_dir
            + " --input_size full_size"
            + " --GPU "
            + gpu1
        )
        scratch_remove_cmd_2 = (
            "python test.py --Scratch_and_Quality_restore --test_input "
            + new_input
            + " --test_mask "
            + new_mask
            + " --outputs_dir "
            + stage_1_output_dir
            + " --gpu_ids "
            + gpu1
        )

        run_cmd(scratch_remove_cmd_1)
        run_cmd(scratch_remove_cmd_2)

   
    stage_1_results = os.path.join(stage_1_output_dir, "restored_image")
    stage_4_output_dir = os.path.join(opts.output_folder, "final_output")
    if not os.path.exists(stage_4_output_dir):
        os.makedirs(stage_4_output_dir)
    for x in os.listdir(stage_1_results):
        img_dir = os.path.join(stage_1_results, x)
        shutil.copy(img_dir, stage_4_output_dir)

    
    
    
    

    print("Running Face Detection")
    os.chdir(".././Face_Detection")
    stage_2_input_dir = os.path.join(stage_1_output_dir, "restored_image")
    stage_2_output_dir = os.path.join(opts.output_folder, "stage_2_detection_output")
    if not os.path.exists(stage_2_output_dir):
        os.makedirs(stage_2_output_dir)
    quality_enhance_cmd = (
        "python detect_face.py --url " + stage_2_input_dir + " --save_url " + stage_2_output_dir
    )
    run_cmd(quality_enhance_cmd)
    

   
    print("Running Face Enhancement")
    os.chdir(".././quality_enhancement")
    stage_3_input_mask = "./"
    stage_3_input_face = stage_2_output_dir
    stage_3_output_dir = os.path.join(opts.output_folder, "stage_3_face_output")
    if not os.path.exists(stage_3_output_dir):
        os.makedirs(stage_3_output_dir)
    quality_enhance_2_cmd = (
        "python test_face.py --old_face_folder "
        + stage_3_input_face
        + " --old_face_label_folder "
        + stage_3_input_mask
        + " --tensorboard_log --name "
        + opts.checkpoint_name
        + " --gpu_ids "
        + gpu1
        + " --load_size 256 --label_nc 18 --no_instance --preprocess_mode resize --batchSize 4 --results_dir "
        + stage_3_output_dir
        + " --no_parsing_map"
    )
    run_cmd(quality_enhance_2_cmd)
   
    

  
    print("Overall Restoration")
    os.chdir(".././Face_Detection")
    stage_4_input_image_dir = os.path.join(stage_1_output_dir, "restored_image")
    stage_4_input_face_dir = os.path.join(stage_3_output_dir, "each_img")
    stage_4_output_dir = os.path.join(opts.output_folder, "final_output")
    if not os.path.exists(stage_4_output_dir):
        os.makedirs(stage_4_output_dir)
    overall_quality_cmd = (
        "python warpback_facedetection.py --origin_url "
        + stage_4_input_image_dir
        + " --replace_url "
        + stage_4_input_face_dir
        + " --save_url "
        + stage_4_output_dir
    )
    run_cmd(overall_quality_cmd)
    
    
    import os

    exec(open('/content/photo_restoration/demo_release.py').read())

    print("  Finished")


