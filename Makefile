SPECS := ice-dkms.spec iavf-dkms.spec
OUTDIR ?= dist/srpm

.PHONY: validate update-upstreams srpm srpm-all srpm-ice srpm-iavf

validate:
	python3 scripts/update-drivers.py --check

update-upstreams:
	python3 scripts/update-drivers.py --write

srpm:
ifndef spec
	$(error pass spec=<name>.spec, for example: make srpm spec=ice-dkms.spec)
endif
	mkdir -p "$(OUTDIR)"
	rpkg srpm --outdir "$(OUTDIR)" --spec "$(spec)"

srpm-all: srpm-ice srpm-iavf

srpm-ice:
	mkdir -p "$(OUTDIR)"
	rpkg srpm --outdir "$(OUTDIR)" --spec ice-dkms.spec

srpm-iavf:
	mkdir -p "$(OUTDIR)"
	rpkg srpm --outdir "$(OUTDIR)" --spec iavf-dkms.spec

