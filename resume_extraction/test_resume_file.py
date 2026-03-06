print("开始测试测试简历文件...")
try:
    from src.extractor import ResumeExtractor
    from src.validators.validator import ResumeValidator
    import os
    
    print("成功导入模块")
    
    # 创建提取器实例
    extractor = ResumeExtractor()
    print("成功创建提取器实例")
    
    # 读取测试简历文件
    resume_file = "examples/test_resume.md"
    if os.path.exists(resume_file):
        print(f"找到测试简历文件: {resume_file}")
        with open(resume_file, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        print(f"文件大小: {len(resume_text)} 字符")
        
        # 提取简历信息
        print("开始提取简历信息...")
        resume = extractor.extract_from_text(resume_text)
        print("提取完成！")
        
        # 转换为CVModel格式
        print("\n=== 转换为CVModel格式 ===")
        cv_model = extractor.to_cv_model(resume, title="test_resume")
        print("转换完成！")
        
        # 打印CVModel结果
        print("\n=== CVModel提取结果 ===")
        print(f"标题: {cv_model.title}")
        print(f"姓名: {cv_model.basic_info.name}")
        print(f"工作年限: {cv_model.basic_info.work_year:.1f}年")
        
        print("\n教育经历:")
        for i, edu in enumerate(cv_model.basic_info.education_experience):
            print(f"  {i+1}. {edu}")
        
        print("\n工作经历:")
        for i, work in enumerate(cv_model.basic_info.work_experience):
            print(f"  {i+1}. {work.job}")
            print(f"     工作年限: {work.year:.1f}年")
            print(f"     工作描述: {work.duty[:100]}...")
        
        print("\n技能:")
        print(f"  {', '.join(cv_model.skills[:10])}{'...' if len(cv_model.skills) > 10 else ''}")
        
        print("\n项目经验:")
        for i, project in enumerate(cv_model.project_experience):
            print(f"  {i+1}. {project[:150]}...")
        
        # 测试验证器
        print("\n=== 验证结果 ===")
        validator = ResumeValidator()
        errors = validator.validate(resume)
        if errors:
            print("验证错误:")
            for key, error_list in errors.items():
                print(f"  {key}:")
                for error in error_list:
                    print(f"    - {error}")
        else:
            print("验证通过，没有错误！")
        
        # 计算数据质量评分
        quality_score = validator.get_data_quality_score(resume)
        print(f"\n数据质量评分: {quality_score:.2f}/100")
        
        print("\n测试完成！")
    else:
        print(f"测试简历文件不存在: {resume_file}")
        print(f"当前目录: {os.getcwd()}")
        print(f"文件列表: {os.listdir('.')}")
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
