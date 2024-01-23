SHELL=/bin/bash
DIR=$(PWD)
SITE_PACKAGES=$(shell scripts/find-site-packages.sh)

clean:
	rm -rf .build

package: clean
	mkdir .build
	pipenv install
	zip -j9 .build/lambda_package.zip src/index/lambda_function.py
	pushd ${SITE_PACKAGES}; \
	zip -r9 ${DIR}/.build/lambda_package.zip .; \
	popd

plan:
	aws-vault exec engcyclopedia --no-session -- terraform -chdir=terraform plan

deploy: package
	cp -R terraform .build
	cp .build/lambda_package.zip .build/terraform
	aws-vault exec engcyclopedia --no-session -- terraform -chdir=.build/terraform init
	aws-vault exec engcyclopedia --no-session -- terraform -chdir=.build/terraform apply
