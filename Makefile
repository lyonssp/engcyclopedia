SHELL=/bin/bash
DIR=$(PWD)

package:
	pushd src/index/package && \
	zip -r ${DIR}/terraform/lambda_package.zip . && \
	popd && \
	pushd src/index && \
	zip ${DIR}/terraform/lambda_package.zip lambda_function.py && \
	popd

plan:
	aws-vault exec sean.lyons --no-session -- terraform -chdir=terraform plan

deploy:
	aws-vault exec sean.lyons --no-session -- terraform -chdir=terraform apply
